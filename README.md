# Tapo P100
Tapo P100 is a Python library for controlling the Tp-link Tapo P100/P105/P110 plugs and L530/L510E bulbs.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install PyP100.

```bash
pip3 install PyP100
```

## Usage
Plugs - P100, P105 etc.
```python
from PyP100 import PyP100

p100 = PyP100.P100("192.168.X.X", "email@gmail.com", "Password123") #Creating a P100 plug object

p100.handshake() #Creates the cookies required for further methods
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods

p100.turnOn() #Sends the turn on request
p100.turnOff() #Sends the turn off request
p100.getDeviceInfo() #Returns dict with all the device info
```
Bulbs - L510E, L530 etc.
```python
from PyP100 import PyL530

l530 = PyL530.L530("192.168.X.X", "email@gmail.com", "Password123") #Creating a L530 bulb object

l530.handshake() #Creates the cookies required for further methods
l530.login() #Sends credentials to the plug and creates AES Key and IV for further methods

#All the bulbs have the PyP100 functions and additionally allows for setting brightness, colour and white temperature
l530.setBrightness(100) #Sends the set brightness request
l530.setColorTemp(2700) #Sets the colour temperature to 2700 Kelvin (Warm White)
l530.setColor(100, 100) #Sends the set colour request
```

Energy Monitoring - P110
```python
from PyP100 import PyP110

p110 = PyP110.P110("192.168.X.X", "email@gmail.com", "Password123") #Creating a P110 plug object

p110.handshake() #Creates the cookies required for further methods
p110.login() #Sends credentials to the plug and creates AES Key and IV for further methods

#PyP110 has all PyP100 functions and additionally allows to query energy usage infos
p110.getEnergyUsage() #Returns dict with all the energy usage
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contributers
[K4CZP3R](https://github.com/K4CZP3R)\
[Sonic74](https://github.com/sonic74)\
[shadow00](https://github.com/shadow00)\
[mochipon](https://github.com/mochipon)\
[realzoulou](https://github.com/realzoulou)\
[arrival-spring](https://github.com/arrival-spring)\
[wlp7s0](https://github.com/wlp7s0)

## License
[MIT](https://choosealicense.com/licenses/mit/)
