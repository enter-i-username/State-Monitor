# State-Monitor
The StateMonitor class can be easily plugged into your deep learning training algorithm, and serve as a hidden state (for example the training losses, validation metrics or even hidden features) monitor. It gathers the infomation within one epoch into a serializable dictionary, and send the serialized binary codes to another process/machine outside this training process through socket communication. Once these serialized scalars and tensors are hooked into some other processes and unraveled, you can independently analyze/visualize them in real time.
# How to use
This package requires `msgpack` to pack a python dictionary into bytes (binary version of json), simply run:
```
pip install msgpack
```
Please note that only numpy arrays are serializable in a dict except for some basic types like int, str and list etc. So if you want to visualize torch tensors, first convert them to np.ndarray. Here is a simple example below.




