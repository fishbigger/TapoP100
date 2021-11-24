from Crypto import Random
from Crypto.Cipher import AES
import hashlib
import pkcs7
import base64


class TpLinkCipher:
    def __init__(self, b_arr: bytearray, b_arr2: bytearray):
        self.iv = b_arr2
        self.key = b_arr

    def mime_encoder(to_encode: bytes):
        encoded_list = list(base64.b64encode(to_encode).decode("UTF-8"))

        count = 0
        for i in range(76, len(encoded_list), 76):
            encoded_list.insert(i + count, '\r\n')
            count += 1
        return ''.join(encoded_list)

    def encrypt(self, data):
        data = pkcs7.PKCS7Encoder().encode(data)
        data: str
        cipher = AES.new(bytes(self.key), AES.MODE_CBC, bytes(self.iv))
        encrypted = cipher.encrypt(data.encode("UTF-8"))
        return TpLinkCipher.mime_encoder(encrypted).replace("\r\n","")

    def decrypt(self, data: str):
        aes = AES.new(bytes(self.key), AES.MODE_CBC, bytes(self.iv))
        pad_text = aes.decrypt(base64.b64decode(data.encode("UTF-8"))).decode("UTF-8")
        return pkcs7.PKCS7Encoder().decode(pad_text)