# State-Monitor
The StateMonitor class can be easily plugged into your deep learning training algorithm, and serve as a hidden state (for example the training losses, validation metrics or even hidden features) monitor. It gathers the infomation needed within one epoch into a serializable dictionary, and send the serialized binary codes to another process/machine outside this training process through socket communication. Once these serialized scalars and tensors are hooked into some other processes and unraveled, you can independently analyze/visualize them in real time.
# How to use
This package requires `msgpack` to pack a python dictionary into bytes (binary version of json), simply run:
```
pip install msgpack
```
Please note that only numpy arrays are serializable in a dict except for some basic types like int, str and list etc. So if you want to visualize torch tensors, first convert them to np.ndarray. Here is a simple example below.
## 1. Initializing
Code for monitor server (where you receive data and visualize them):
```python
host_monitor = StateMonitor(mode='host', host='localhost', port=10086, verbose=True)
host_monitor.start()
```
Code for client (where you are training the network and data of interest is sent from here):
```python
client_monitor = StateMonitor(mode='client', host='localhost', port=10086, verbose=True)
client_monitor.start()
```
By starting the host monitor and client monitor sequentially, they connect to each other and get ready to perform data transmission.
## 2. Plugging client monitor into training code snippet


```python
for x_batch, y_batch in dataloader:

```
