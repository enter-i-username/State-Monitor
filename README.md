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
    # Standard backward propagation algorithm in one epoch
    x_batch, y_batch = x_batch.to(device), y_batch.to(device)
    output, hidden_features = model(x_batch)
    loss = criterion(output, hidden_features, y_batch)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # To plug the client monitor obj, first construct the data dictionary
    losses.append(float(loss))
    data_dict = {
        'epoch': e,
        'losses': losses,
        'output': output.cpu().detach().numpy(),
        'hidden_features': hidden_features.cpu().detach().numpy(),
    }
    # The monitor will automatically encode data_dict into bytes and
    # send them to the server, just using the following one line:
    client_monitor.put(data_dict)
```
Note that `client_monitor.put(data_dict)` will only push the dict into a queue and the serialization and transmission will be running in a separate thread (non-blocking here), which means it will not take much time in the training process.

