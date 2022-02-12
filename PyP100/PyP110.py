from PyP100 import PyP100

import json
import logging
import time

_LOGGER = logging.getLogger(__name__)

class P110(PyP100.P100):

    def getEnergyUsage(self):
        URL = f"http://{self.ipAddress}/app?token={self.token}"
        Payload = {
            "method": "get_energy_usage",
            "requestTimeMils": int(round(time.time() * 1000)),
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

        return json.loads(decryptedResponse)
