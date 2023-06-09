from PyP100 import PyP100

import json
import logging
import time
import ast

from PyP100.TapoError import TapoError

_LOGGER = logging.getLogger(__name__)

class P110(PyP100.P100):

    def getEnergyUsage(self):
        URL = f"http://{self.ipAddress}/app?token={self.token}"
        Payload = {
            "method": "get_energy_usage",
            "requestTimeMils": 0,
        }

        headers = {
            "Cookie": self.cookie
        }

        EncryptedPayload = self.tpLinkCipher.encrypt(json.dumps(Payload))

        SecurePassthroughPayload = {
            "method":"securePassthrough",
            "params":{
                "request": EncryptedPayload
            }
        }
        _LOGGER.debug("getEnergyUsage %s", self.ipAddress)
        r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers, timeout=2)

        decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

        if ast.literal_eval(decryptedResponse)["error_code"] != 0:
            errorCode = ast.literal_eval(decryptedResponse)["error_code"]
            errorMessage = self.errorCodes[str(errorCode)]
            raise TapoError(errorCode, errorMessage)

        return json.loads(decryptedResponse)
