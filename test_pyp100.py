import os

from PyP100 import PyP100
import logging
from logging.config import fileConfig
import unittest



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
# Name of device; used in some tests ok to not set
TP_DEVICE_NAME = "TP_DEVICE_NAME"


tp_email = None
tp_pass = None

tp_device = None
tp_device_name = None
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
		self.tp_device_name = getvar(TP_DEVICE_NAME)

	def bind(self):
		self.initVars()
		self.assertIsNotNone(self.tp_email,"No email")
		self.assertIsNotNone(self.tp_pass,"No pass")
		self.assertIsNotNone(self.tp_device,"No device")
		p100 = PyP100.P100(self.tp_device, self.tp_email, self.tp_pass) #Creating a P100 plug object
		p100.handshake() #Creates the cookies required for further methods
		return p100

	def testPasswordLengthOK(self):
		"""Assert password length is good"""
		self.initVars()
		self.assertLessEqual(len(self.tp_pass), 8,
				     "Password string too long for device authentication")

	def testHandshake(self):
		"""Test basic hanshake"""
		self.bind()

	def testPower(self):
		p100 = self.bind()
		p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
		p100.turnOn() #Sends the turn on request
		p100.setBrightness(100) #Sends the set brightness request
		p100.turnOff() #Sends the turn off request
		info = p100.getDeviceInfo()
		self.logger.info("Device %s", info)

	def testInfo(self):
		p100 = self.bind()
		devinfo = p100.getDeviceInfo() #Returns dict with all the device info
		print(devinfo)

	def testDeviceList(self):
		p100 = self.bind()
		devices = p100.listDevices()
		print(devices)



if __name__ == '__main__':
	unittest.main()