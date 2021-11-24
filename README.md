# Tapo P100
Tapo P100 is a Python library for controlling the Tp-link Tapo P100 plugs, P105 plugs and L510E bulbs.

## Installation

coming soon...

## Usage

```python
from PyP100 import PyP100

p100 = PyP100.P100("192.168.X.X", "email@gmail.com", "Password123") #Creating a P100 plug object

p100.handshake() #Creates the cookies required for further methods 
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods

p100.turnOn() #Sends the turn on request
p100.setBrightness(100) #Sends the set brightness request
p100.turnOff() #Sends the turn off request
p100.getDeviceInfo() #Returns dict with all the device info


```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contributers

## License
[MIT](https://choosealicense.com/licenses/mit/)
