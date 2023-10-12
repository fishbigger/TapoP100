# PyP100

PyP100 is a Python library for controlling many of the TP-Link Tapo devices including the P100, P105, P110 plugs and the
L530 and L510E bulbs.

This fork is designed exclusively to support the new authentication method and is currently compatible with the P100
version 1.2.2.

Most of the code originates from [OctoPrint-PSUControl-Tapo](https://github.com/dswd/OctoPrint-PSUControl-Tapo).

At the moment, it offers only basic switch on/off functionality. If you wish to expand its features, please feel free to
fork and enhance it.

## Installation

PyP100 can be installed using the package manager [pip](https://pip.pypa.io/en/stable/).

```bash
  pip install git+https://github.com/almottier/TapoP100.git
```

## Usage

#### Plugs - P100, P105 etc.

```python
from PyP100 import PyP100

p100 = PyP100.P100("192.168.X.X", "email@gmail.com", "Password123")  # Creates a P100 plug object

p100.turnOn()  # Turns the connected plug on
p100.turnOff()  # Turns the connected plug off
p100.toggleState()  # Toggles the state of the connected plug

p100.getDeviceInfo()  # Returns dict with all the device info of the connected plug
p100.getDeviceName()  # Returns the name of the connected plug set in the app

p100.handshake()  # DEPRECATED
p100.login()  # DEPRECATED
```

#### Bulbs - L530, L510E etc.

```python
from PyP100 import PyL530

l530 = PyL530.L530("192.168.X.X", "email@gmail.com", "Password123")
```

#### Energy Monitoring - P110

```python
from PyP100 import PyP110

p110 = PyP110.P110("192.168.X.X", "email@gmail.com", "Password123")
```

## Contributing

Contributions are always welcome!

Please submit a pull request or open an issue for any changes.

## License

[MIT](https://choosealicense.com/licenses/mit/)

