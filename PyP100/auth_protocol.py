import logging
import requests
from Crypto.Hash import SHA256, SHA1
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
import json


log = logging.getLogger(__name__)


def sha1(data: bytes) -> bytes:
    return SHA1.new(data).digest()


def sha256(data: bytes) -> bytes:
    return SHA256.new(data).digest()


class AuthProtocol:
    def __init__(self, address: str, username: str, password: str):
        self.session = requests.Session()  # single session, stores cookie
        self.address = address
        self.username = username
        self.password = password
        self.key = None
        self.iv = None
        self.seq = None
        self.sig = None

    def calc_auth_hash(self, username: str, password: str) -> bytes:
        return sha256(sha1(username.encode()) + sha1(password.encode()))

    def _request_raw(self, path: str, data: bytes, params: dict = None):
        url = f"http://{self.address}/app/{path}"
        resp = self.session.post(url, data=data, timeout=2, params=params)
        resp.raise_for_status()
        data = resp.content
        return data

    def _request(self, method: str, params: dict = None):
        if not self.key:
            self.Initialize()
        payload = {
            "method": method
        }
        if params:
            payload["params"] = params
        log.debug(f"Request: {payload}")
        # Encrypt payload and execute call
        encrypted = self._encrypt(json.dumps(payload).encode("UTF-8"))
        result = self._request_raw("request", encrypted, params={"seq": self.seq})
        # Unwrap and decrypt result
        data = json.loads(self._decrypt(result).decode("UTF-8"))
        # Check error code and get result
        if data["error_code"] != 0:
            log.error(f"Error: {data}")
            self.key = None
            raise Exception(f"Error code: {data['error_code']}")
        result = data.get("result")
        log.debug(f"Response: {result}")
        return result

    def _encrypt(self, data: bytes):
        self.seq += 1
        seq = self.seq.to_bytes(4, "big", signed=True)
        # Add PKCS#7 padding
        pad_l = 16 - (len(data) % 16)
        data = data + bytes([pad_l] * pad_l)
        # Encrypt data with key
        crypto = AES.new(self.key, AES.MODE_CBC, self.iv + seq)
        ciphertext = crypto.encrypt(data)
        # Signature
        sig = sha256(self.sig + seq + ciphertext)
        return sig + ciphertext

    def _decrypt(self, data: bytes):
        # Decrypt data with key
        seq = self.seq.to_bytes(4, "big", signed=True)
        crypto = AES.new(self.key, AES.MODE_CBC, self.iv + seq)
        data = crypto.decrypt(data[32:])

        # Remove PKCS#7 padding
        data = data[:-data[-1]]
        return data

    def Initialize(self):
        local_seed = get_random_bytes(16)
        response = self._request_raw("handshake1", local_seed)
        remote_seed, server_hash = response[0:16], response[16:]
        auth_hash = None
        for creds in [(self.username, self.password), ("", ""), ("kasa@tp-link.net", "kasaSetup")]:
            ah = self.calc_auth_hash(*creds)
            local_seed_auth_hash = sha256(local_seed + remote_seed + ah)
            if local_seed_auth_hash == server_hash:
                auth_hash = ah
                log.debug(f"Authenticated with {creds[0]}")
                break
        if not auth_hash:
            raise Exception("Failed to authenticate")
        self._request_raw("handshake2", sha256(remote_seed + local_seed + auth_hash))
        self.key = sha256(b"lsk" + local_seed + remote_seed + auth_hash)[:16]
        ivseq = sha256(b"iv" + local_seed + remote_seed + auth_hash)
        self.iv = ivseq[:12]
        self.seq = int.from_bytes(ivseq[-4:], "big", signed=True)
        self.sig = sha256(b"ldk" + local_seed + remote_seed + auth_hash)[:28]
        log.debug(f"Initialized")
