# State-Monitor
The StateMonitor class can be easily plugged into your deep learning training algorithm, and serve as a hidden state (for example the training losses, validation metrics or even hidden features) monitor. It captures the infomation within one epoch, and send them to another process/machine outside this training process through socket communication.
