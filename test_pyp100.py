import os
from PyP100 import PyP100
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

tp_email = None
tp_pass = None
tp_device = None

def getvar(name):
    val = os.environ.get(name)
    if val is None:
        print("Unset environment variable ", name)
    else:
        print("Env var %s is %s" % (name, val))
    return val


def initVars():
    tp_email = getvar(TP_EMAIL)
    tp_pass = getvar(TP_PASS)
    tp_device = getvar(TP_DEVICE)

def bind():
    p100 = PyP100.P100(tp_device, tp_email, tp_pass) #Creating a P100 plug object
    p100.handshake() #Creates the cookies required for further methods
    p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
    return p100


class TestPy100(unittest.TestCase):

    def setUp(self):
        initVars()


    def testEmailSet(self):
        """todo"""

    def testBinding(self):
        bind()

    def testPower(self):
        p100 = bind()
        p100.turnOn() #Sends the turn on request
        p100.setBrightness(100) #Sends the set brightness request
        p100.turnOff() #Sends the turn off request
        p100.getDeviceInfo() #Returns dict with all the device info

    def testInfo(self):
        p100 = bind()
        devinfo = p100.getDeviceInfo() #Returns dict with all the device info
        print(devinfo)



if __name__ == '__main__':
    unittest.main()