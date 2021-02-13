import os

from PyP100 import PyP100
import unittest
import logging
from logging.config import fileConfig



"""
Integration test for the py100 module.

This needs a set of credentials and a plug to turn on and off.
These are set in env vars to avoid config reading code.
"""

# Email address
TP_EMAIL = "TP_EMAIL"
# password
TP_PASS = "TP_PASS"
# IP addr of test device
TP_DEVICE = "TP_DEVICE"

tp_email = None
tp_pass = None
tp_device = None
fileConfig('logging-config.ini')


def getvar(name):
	val = os.environ.get(name)
	if val is None:
		print(f"Unset environment variable {name}")
	else:
		print(f"Env var {name} is {val}")
	return val


class TestPy100(unittest.TestCase):

	def setUp(self):
		self.logger = logging.getLogger("p100")
		print("setup")

	def initVars(self):
		self.tp_email = getvar(TP_EMAIL)
		self.tp_pass = getvar(TP_PASS)
		self.tp_device = getvar(TP_DEVICE)

	def bind(self):
		self.initVars()
		self.assertIsNotNone(self.tp_email,"No email")
		self.assertIsNotNone(self.tp_pass,"No pass")
		self.assertIsNotNone(self.tp_device,"No device")
		p100 = PyP100.P100(self.tp_device, self.tp_email, self.tp_pass) #Creating a P100 plug object
		p100.handshake() #Creates the cookies required for further methods
		return p100


	def testHandshake(self):
		self.bind()

	def testPower(self):
		p100 = self.bind()
		p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
		p100.turnOn() #Sends the turn on request
		p100.setBrightness(100) #Sends the set brightness request
		p100.turnOff() #Sends the turn off request
		p100.getDeviceInfo() #Returns dict with all the device info

	def testInfo(self):
		p100 = self.bind()
		devinfo = p100.getDeviceInfo() #Returns dict with all the device info
		print(devinfo)



if __name__ == '__main__':
	unittest.main()