from PyP100 import PyP110
import os
from flask import Flask
p110 = PyP110.P110(os.environ.get('IP_ADDRESS'),
                   os.environ.get('EMAIL'),
                   os.environ.get('PASSWORD'))
p110.handshake()
p110.login()
app = Flask(__name__)
@app.route('/info')
def info():
    return p110.getDeviceInfo()
@app.route('/usage')
def usage():
    return p110.getEnergyUsage()
app.run(host='0.0.0.0')
