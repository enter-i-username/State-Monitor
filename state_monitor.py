import socket
from queue import Empty, Full
from . import array_packer


class StateMonitor:

    MAX_BYTES_LEN = 1024 * 1024 * 1024
    MAX_QUEUE_LEN = 100

    @staticmethod
    def queue_full_put(q, elem):
        try:
            q.put_nowait(elem)
        except Full:
            _ = q.get_nowait()
            q.put_nowait(elem)

    class ProcessType:

        class Process:
            import multiprocessing
            Process = multiprocessing.Process
            Queue = multiprocessing.Queue

        class Thread:
            import threading
            import queue
            Process = threading.Thread
            Queue = queue.Queue

    class _SharedSpace:
        def create_process(self, *args):
            *others, process_type, process_callback = args

            process = process_type.Process(
                target=process_callback,
                args=others
            )
            return process

    # In host mode
    class _HostSpace(_SharedSpace):
        def create_connected_socket(self, *args):
            host, port, print_cb = args

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((host, port))
            sock.listen(5)

            print_cb('Waiting for client connecting...')
            connected_sock, addr = sock.accept()
            print_cb(f'Client @ {addr} connected!')

            return connected_sock

        def create_process(self, *args):
            msg_queue, sock, process_type = args
            return super(StateMonitor._HostSpace, self).create_process(
                msg_queue, sock, process_type, self._host_process_callback
            )

        @staticmethod
        def _host_process_callback(msg_queue, sock):
            # listen to sock and send msg to msg_queue
            while True:
                try:  # if something wrong with the sock
                    binary_code = sock.recv(StateMonitor.MAX_BYTES_LEN)
                    msg_dict = array_packer.unpack_dict(binary_code)
                    if msg_dict is not None:
                        StateMonitor.queue_full_put(msg_queue, msg_dict)

                except:
                    pass  # not yet implemented

    # In client mode
    class _ClientSpace(_SharedSpace):
        def create_connected_socket(self, *args):
            host, port, print_cb = args

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            print_cb(f'Connecting to host @ {(host, port)}...')
            sock.connect((host, port))
            print_cb(f'Host connected!')

            return sock

        def create_process(self, *args):
            msg_queue, sock, process_type = args
            return super(StateMonitor._ClientSpace, self).create_process(
                msg_queue, sock, process_type, self._client_process_callback
            )

        @staticmethod
        def _client_process_callback(msg_queue, sock):
            # listen to msg_queue and send msg to sock
            while True:
                try:
                    # get msg_dict from another process
                    msg_dict = msg_queue.get_nowait()
                    # check np arrays and serialize msg_dict
                    binary_code = array_packer.pack_dict(msg_dict)
                    # make sure len <= max
                    if len(binary_code) <= StateMonitor.MAX_BYTES_LEN:
                        # send...
                        try:  # if something wrong with the socket
                            sock.send(binary_code)
                        except:
                            pass  # not yet implemented
                    else:
                        pass  # not yet implemented
                except Empty:
                    pass

    def __init__(self, **kwargs):
        self.mode = kwargs['mode'].lower()
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.verbose = kwargs.get('verbose', False)
        self.print_cb = kwargs.get('print_cb', StateMonitor.default_print_cb)
        self.process_type = kwargs.get('process_type', StateMonitor.ProcessType.Thread)

        self.space = self._HostSpace() if self.mode == 'host' else self._ClientSpace()

        self.msg_queue = self.process_type.Queue(maxsize=StateMonitor.MAX_QUEUE_LEN)

        self.running = False

    def start(self):
        # Connect in blocking mode
        sock = self.space.create_connected_socket(
            self.host, self.port, lambda _str: self.print_cb(_str, self.verbose)
        )
        # Create and start
        setattr(self, 'listening_process',
                self.space.create_process(self.msg_queue, sock, self.process_type))
        getattr(self, 'listening_process').start()

        self.running = True
        self.print_cb('Monitor permanently running...', self.verbose)

    def end(self):
        # not yet implemented
        # maybe i should find some way to break out of the blocked process...
        pass

    def get(self):
        if self.mode != 'host':
            raise NotImplementedError(f"'get' method can be used ONLY in host mode.")
        if not self.running:
            raise Exception('Monitor not started')

        # receive msg_dict in non-blocking mode
        try:
            msg_dict = self.msg_queue.get_nowait()
            return msg_dict
        except Empty:
            return None

    def put(self, msg_dict):
        if self.mode != 'client':
            raise NotImplementedError(f"'put' method can be used ONLY in client mode.")
        if not self.running:
            raise Exception('Monitor not started')

        # note that in multiprocess mode, 'put' will pass a deep copy of msg_dict;
        # however in threading mode, 'put' only passes its reference.
        StateMonitor.queue_full_put(self.msg_queue, msg_dict)

    @staticmethod
    def default_print_cb(string, verbose):
        if verbose:
            print(string)


