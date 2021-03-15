import requests
from base64 import b64encode, b64decode
import hashlib
from Crypto.PublicKey import RSA
import time
import json
from Crypto.Cipher import AES, PKCS1_OAEP, PKCS1_v1_5
from . import tp_link_cipher
import ast
import pkgutil
import logging

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
	"-1501": "Invalid Request or Credentials",
	"1002": "Incorrect Request",
	"-1003": "JSON formatting error",
	"-1009": "GET not supported?"
}

class P100():
	def __init__ (self, ipAddress, email, password):
		self.ipAddress = ipAddress

		self.email = email
		self.password = password

		self.errorCodes = ERROR_CODES

		self.encryptCredentials(email, password)
		self.createKeyPair()
		self.logger = logging.getLogger("p100")
		self.logger.info("Email %s", email)
		self.token = "not logged in yet"

	def encryptCredentials(self, email, password):
		#Password Encoding
		self.encodedPassword = tp_link_cipher.TpLinkCipher.mime_encoder(password.encode("utf-8"))

		#Email Encoding
		self.encodedEmail = self.sha_digest_username(email)
		self.encodedEmail = tp_link_cipher.TpLinkCipher.mime_encoder(self.encodedEmail.encode("utf-8"))

	def createKeyPair(self):
		self.keys = RSA.generate(1024)

		self.privateKey = self.keys.exportKey("PEM")
		self.publicKey  = self.keys.publickey().export_key("PEM")

	def decode_handshake_key(self, key):
		decode: bytes = b64decode(key.encode("UTF-8"))
		decode2: bytes = self.privateKey

		cipher = PKCS1_v1_5.new(RSA.import_key(decode2))
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
				"requestTimeMils": int(round(time.time() * 1000))
			}
		}

		self.logger.info("Posting to %s:%s", URL, Payload)
		r = requests.post(URL, json=Payload)

		encryptedKey = r.json()["result"]["key"]
		self.tpLinkCipher = self.decode_handshake_key(encryptedKey)

		try:
			self.cookie = r.headers["Set-Cookie"][:-13]
			self.logger.info(f"Handshake completed; cookie={self.cookie}")
		except:
			errorCode = r.json()["error_code"]
			errorMessage = self.lookupErrorCode[str(errorCode)]
			raise Exception(f"Error Code: {errorCode}, {errorMessage}")

	def login(self):
		URL = f"http://{self.ipAddress}/app"
		Payload = {
			"method":"login_device",
			"params":{
				"username": self.encodedEmail,
				"password": self.encodedPassword
			},
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

		self.logger.info(f"Login request {SecurePassthroughPayload}")
		r = requests.post(URL, json=SecurePassthroughPayload, headers=headers)

		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])
		self.logger.info(f"login response {decryptedResponse}")

		try:
			self.token = ast.literal_eval(decryptedResponse)["result"]["token"]
		except:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			errorMessage = self.lookupErrorCode[str(errorCode)]
			raise Exception(f"Error Code: {errorCode}, {errorMessage}")

	def turnOn(self):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "set_device_info",
			"params":{
				"device_on": True
			},
			"requestTimeMils": int(round(time.time() * 1000)),
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

		r = requests.post(URL, json=SecurePassthroughPayload, headers=headers)

		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		if ast.literal_eval(decryptedResponse)["error_code"] != 0:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			raise self.error("turnOn", str(errorCode))


	def setBrightness(self, brightness):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "set_device_info",
			"params":{
				"brightness": brightness
			},
			"requestTimeMils": int(round(time.time() * 1000)),
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

		r = requests.post(URL, json=SecurePassthroughPayload, headers=headers)

		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		if ast.literal_eval(decryptedResponse)["error_code"] != 0:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			raise self.error("setBrightness", str(errorCode))

	def turnOff(self):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "set_device_info",
			"params":{
				"device_on": False
			},
			"requestTimeMils": int(round(time.time() * 1000)),
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

		r = requests.post(URL, json=SecurePassthroughPayload, headers=headers)

		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		if ast.literal_eval(decryptedResponse)["error_code"] != 0:
			errorCode = ast.literal_eval(decryptedResponse)["error_code"]
			raise self.error("turnOff", str(errorCode))

	def getDeviceInfo(self):
		URL = f"http://{self.ipAddress}/app?token={self.token}"
		Payload = {
			"method": "get_device_info",
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

		r = requests.post(URL, json=SecurePassthroughPayload, headers=headers)



		decryptedResponse = self.tpLinkCipher.decrypt(r.json()["result"]["response"])

		return decryptedResponse

	def getDeviceName(self):
		self.handshake()
		self.login()
		data = self.getDeviceInfo()

		data = json.loads(data)

		if data["error_code"] != 0:
			errorCode = ast.literal_eval(data)["error_code"]
			raise self.error("get_device_info", str(errorCode))
		else:
			encodedName = data["result"]["nickname"]
			name = b64decode(encodedName)
			return name.decode("utf-8")

	def listDevices(self):
		return getDeviceList(self.email, self.password)

	def error(self, action: str, errorCode: str) -> Exception:
		"""report an error: log it and save the self. fields"""
		sec = str(errorCode)
		self.lastErrorCode = sec
		errorMessage = self.lookupErrorCode(sec)
		self.lastErrorMessage = errorMessage
		self.logger.warning("Error %s: %s: %s", action, sec, errorMessage)
		return Exception(f"Error Code: {errorCode}, {errorMessage}")

	def lookupErrorCode(self, errorCode: str) -> str:
		""" Look up an error code, fall back to the number if the code is unknown """
		s = self.errorCodes[errorCode]
		if s is None:
			return "Error " + errorCode
		else:
			return s
