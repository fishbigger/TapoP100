import requests
from requests import Session
from .TapoError import TapoError

from base64 import b64encode, b64decode
import hashlib
from Crypto.PublicKey import RSA
import time
import json
from Crypto.Cipher import AES, PKCS1_OAEP, PKCS1_v1_5
from . import tp_link_cipher
import ast
import pkgutil
import uuid
import json


#Old Functions to get device list from tplinkcloud
def getToken(email, password):
	URL = "https://eu-wap.tplinkcloud.com"
	Payload = {
		"method": "login",
		"params": {
			"appType": "Tapo_Ios",
			"cloudUserName": email,
			"cloudPassword": password,
			"terminalUUID": "0A950402-7224-46EB-A450-7362CDB902A2"
		}
	}

	return requests.post(URL, json=Payload).json()['result']['token']

def getDeviceList(email, password):
	URL = "https://eu-wap.tplinkcloud.com?token=" + getToken(email, password)
	Payload = {
		"method": "getDeviceList",
	}

	return requests.post(URL, json=Payload).json()

ERROR_CODES = {
	"0": "Success",
	"-1010": "Invalid Public Key Length",
	"-1012": "Invalid terminalUUID",
	"-1501": "Invalid Request or Credentials",
	"1002": "Incorrect Request",
	"-1003": "JSON formatting error "
}

class P100():
	def __init__ (self, ipAddress, email, password):
		self.ipAddress = ipAddress
		self.terminalUUID = str(uuid.uuid4())

		self.email = email
		self.password = password
		self.session = None
		self.cookie_name = "TP_SESSIONID"

		self.errorCodes = ERROR_CODES

		self.encryptCredentials()
		self.createKeyPair()

	def encryptCredentials(self):
		#Password Encoding
		self.encodedPassword = b64encode(self.password.encode("UTF-8")).decode("UTF-8")

		#Email Encoding
		self.encodedEmail = self.sha_digest_username(self.email)
		self.encodedEmail = b64encode(self.encodedEmail.encode("utf-8")).decode("UTF-8")

	def createKeyPair(self):
		self.keys = RSA.generate(1024)

		self.privateKey = self.keys.exportKey("PEM")
		self.publicKey  = self.keys.publickey().exportKey("PEM")

	def decode_handshake_key(self, key):
		decode: bytes = b64decode(key.encode("UTF-8"))
		decode2: bytes = self.privateKey

		cipher = PKCS1_v1_5.new(RSA.importKey(decode2))
		do_final = cipher.decrypt(decode, None)
		if do_final is None:
			raise ValueError("Decryption failed!")

		b_arr:bytearray = bytearray()
		b_arr2:bytearray = bytearray()

		for i in range(0, 16):
			b_arr.insert(i, do_final[i])
		for i in range(0, 16):
			b_arr2.insert(i, do_final[i + 16])

		return tp_link_cipher.TpLinkCipher(b_arr, b_arr2)

	def sha_digest_username(self, data):
		b_arr = data.encode("UTF-8")
		digest = hashlib.sha1(b_arr).digest()

		sb = ""
		for i in range(0, len(digest)):
			b = digest[i]
			hex_string = hex(b & 255).replace("0x", "")
			if len(hex_string) == 1:
				sb += "0"
				sb += hex_string
			else:
				sb += hex_string

		return sb

	def handshake(self):
		URL = f"http://{self.ipAddress}/app"
		Payload = {
			"method":"handshake",
			"params":{
				"key": self.publicKey.decode("utf-8"),
				"requestTimeMils": 0
			}
		}
		# start new TCP session
		if self.session:
			self.session.close()
		self.session = Session()

		r = self.session.post(URL, json=Payload, timeout=2)

		encryptedKey = r.json()["result"]["key"]
		self.tpLinkCipher = self.decode_handshake_key(encryptedKey)

		try:
			self.cookie = f"{self.cookie_name}={r.cookies[self.cookie_name]}"

		except:
			errorCode = r.json()["error_code"]
			errorMessage = self.errorCodes[str(errorCode)]
			raise TapoError(errorCode, errorMessage)

	def login(self):
		URL = f"http://{self.ipAddress}/app"
		Payload = {
			"method":"login_device",
			"params":{
				"password": self.encodedPassword,
				"username": self.encodedEmail
			},
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

		r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers, timeout=2)

		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		try:
			self.token = ast.literal_eval(decryptedResponse)["result"]["token"]
		except:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			errorMessage = self.errorCodes[str(errorCode)]
			raise TapoError(errorCode, errorMessage)

	def turnOn(self):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "set_device_info",
			"params":{
				"device_on": True
			},
			"requestTimeMils": 0,
			"terminalUUID": self.terminalUUID
		}

		headers = {
			"Cookie": self.cookie
		}

		EncryptedPayload = self.tpLinkCipher.encrypt(json.dumps(Payload))

		SecurePassthroughPayload = {
			"method": "securePassthrough",
			"params": {
				"request": EncryptedPayload
			}
		}

		r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers, timeout=2)

		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		if ast.literal_eval(decryptedResponse)["error_code"] != 0:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			errorMessage = self.errorCodes[str(errorCode)]
			raise TapoError.TapoError(errorCode, errorMessage)

	def turnOff(self):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "set_device_info",
			"params":{
				"device_on": False
			},
			"requestTimeMils": 0,
			"terminalUUID": self.terminalUUID
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
			raise TapoError.TapoError(errorCode, errorMessage)

	def getDeviceInfo(self):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "get_device_info",
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

		r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers)
		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		if ast.literal_eval(decryptedResponse)["error_code"] != 0:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			errorMessage = self.errorCodes[str(errorCode)]
			raise TapoError.TapoError(errorCode, errorMessage)

		return json.loads(decryptedResponse)

	def getDeviceName(self):
		data = self.getDeviceInfo()

		encodedName = data["result"]["nickname"]
		name = b64decode(encodedName)
		return name.decode("utf-8")

	def toggleState(self):
		state = self.getDeviceInfo()["result"]["device_on"]
		if state:
			self.turnOff()
		else:
			self.turnOn()

	def turnOnWithDelay(self, delay):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "add_countdown_rule",
			"params": {
				"delay": int(delay),
				"desired_states": {
					"on": True
				},
				"enable": True,
				"remain": int(delay)
			},
			"terminalUUID": self.terminalUUID
		}

		headers = {
			"Cookie": self.cookie
		}

		EncryptedPayload = self.tpLinkCipher.encrypt(json.dumps(Payload))

		SecurePassthroughPayload = {
			"method": "securePassthrough",
			"params": {
				"request": EncryptedPayload
			}
		}

		r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers)

		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		if ast.literal_eval(decryptedResponse)["error_code"] != 0:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			errorMessage = self.errorCodes[str(errorCode)]
			raise TapoError.TapoError(errorCode, errorMessage)

	def turnOffWithDelay(self, delay):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "add_countdown_rule",
			"params": {
				"delay": int(delay),
				"desired_states": {
					"on": False
				},
				"enable": True,
				"remain": int(delay)
			},
			"terminalUUID": self.terminalUUID
		}

		headers = {
			"Cookie": self.cookie
		}

		EncryptedPayload = self.tpLinkCipher.encrypt(json.dumps(Payload))

		SecurePassthroughPayload = {
			"method": "securePassthrough",
			"params": {
				"request": EncryptedPayload
			}
		}

		r = self.session.post(URL, json=SecurePassthroughPayload, headers=headers)

		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		if ast.literal_eval(decryptedResponse)["error_code"] != 0:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			errorMessage = self.errorCodes[str(errorCode)]
			raise TapoError.TapoError(errorCode, errorMessage)
