
# PyP100

PyP100 is a Python library for controlling many of the TP-Link Tapo devices including the P100, P105, P110 plugs and the L530 and L510E bulbs.


## Support

If you would like to support the project, please consider buying me a coffee.

<a href="https://www.buymeacoffee.com/fishbigger" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>


## Installation

PyP100 can be installed using the package manager [pip](https://pip.pypa.io/en/stable/).

```bash
  pip install PyP100
```
    

## Usage

#### Plugs - P100, P105 etc.
```python
from PyP100 import PyP100

p100 = PyP100.P100("192.168.X.X", "email@gmail.com", "Password123") #Creates a P100 plug object

p100.handshake() #Creates the cookies required for further methods
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods

p100.turnOn() #Turns the connected plug on
p100.turnOff() #Turns the connected plug off
p100.toggleState() #Toggles the state of the connected plug

p100.turnOnWithDelay(10) #Turns the connected plug on after 10 seconds
p100.turnOffWithDelay(10) #Turns the connected plug off after 10 seconds

p100.getDeviceInfo() #Returns dict with all the device info of the connected plug
p100.getDeviceName() #Returns the name of the connected plug set in the app
```

#### Bulbs - L530, L510E etc.
```python
from PyP100 import PyL530

l530 = PyL530.L530("192.168.X.X", "email@gmail.com", "Password123")

l530.handshake() #Creates the cookies required for further methods
l530.login() #Sends credentials to the plug and creates AES Key and IV for further methods

#All the bulbs have the same basic functions as the plugs and additionally allow for the following functions.
l530.setBrightness(50) #Sets the brightness of the connected bulb to 50% brightness
l530.setColorTemp(2700) #Sets the color temperature of the connected bulb to 2700 Kelvin (Warm White)
l530.setColor(30, 80) #Sets the color of the connected bulb to Hue: 30°, Saturation: 80% (Orange)
```

#### Energy Monitoring - P110
```python
from PyP100 import PyP110

p110 = PyP100.P110("192.168.X.X", "email@gmail.com", "Password123")

p110.handshake() #Creates the cookies required for further methods
p110.login() #Sends credentials to the plug and creates AES Key and IV for further methods

#The P110 has all the same basic functions as the plugs and additionally allow for energy monitoring.
p110.getEnergyUsage() #Returns dict with all of the energy usage of the connected plug
```

## Contributing

Contributions are always welcome!

Please submit a pull request or open an issue for any changes.


## License

[MIT](https://choosealicense.com/licenses/mit/)

