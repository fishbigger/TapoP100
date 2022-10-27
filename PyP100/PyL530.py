from PyP100 import PyP100

import json
import logging
import time
import ast

_LOGGER = logging.getLogger(__name__)

class L530(PyP100.P100):
    def setBrightness(self, brightness):
        self.turnOn()
        URL = f"http://{self.ipAddress}/app?token={self.token}"
        Payload = {
			"method": "set_device_info",
			"params":{
				"brightness": brightness
			},
			"requestTimeMils": 0,
		}

        headers = {
			"Cookie": self.cookie
		}

        EncryptedPayload = self.tpLinkCipher.encrypt(json.dumps(Payload))

        SecurePassthroughPayload = {
			"method": "securePassthrough",
			"params":{
				"request": EncryptedPayload
			}
		}

        r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers, timeout=2)

        decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

        if ast.literal_eval(decryptedResponse)["error_code"] != 0:
            errorCode = ast.literal_eval(decryptedResponse)["error_code"]
            errorMessage = self.errorCodes[str(errorCode)]
            raise Exception(f"Error Code: {errorCode}, {errorMessage}")

    def setColorTemp(self, colortemp):
        self.turnOn()
        URL = f"http://{self.ipAddress}/app?token={self.token}"
        Payload = {
        	"method": "set_device_info",
        	"params":{
        		"color_temp": colortemp
        	},
        	"requestTimeMils": 0,
        }

        headers = {
        	"Cookie": self.cookie
        }

        EncryptedPayload = self.tpLinkCipher.encrypt(json.dumps(Payload))

        SecurePassthroughPayload = {
        	"method": "securePassthrough",
        	"params":{
        		"request": EncryptedPayload
        	}
        }

        r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers, timeout=2)

        decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

        if ast.literal_eval(decryptedResponse)["error_code"] != 0:
        	errorCode = ast.literal_eval(decryptedResponse)["error_code"]
        	errorMessage = self.errorCodes[str(errorCode)]

    def setColor(self, hue, saturation):
        self.turnOn()
        self.setColorTemp(0)

        URL = f"http://{self.ipAddress}/app?token={self.token}"
        Payload = {
        	"method": "set_device_info",
        	"params":{
        		"hue": hue,
        		"saturation": saturation
        	},
        	"requestTimeMils": 0,
        }

        headers = {
        	"Cookie": self.cookie
        }

        EncryptedPayload = self.tpLinkCipher.encrypt(json.dumps(Payload))

        SecurePassthroughPayload = {
        	"method": "securePassthrough",
        	"params":{
        		"request": EncryptedPayload
        	}
        }

        r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers, timeout=2)

        decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

        if ast.literal_eval(decryptedResponse)["error_code"] != 0:
        	errorCode = ast.literal_eval(decryptedResponse)["error_code"]
        	errorMessage = self.errorCodes[str(errorCode)]
