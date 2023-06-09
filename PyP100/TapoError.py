import requests


class TapoError(Exception):
	"""
	Exception raised when an error code is present in the response from a Tapo device
	"""

	def __init__(self, errorCode, errorMessage):
		self.errorCode = errorCode
		self.errorMessage = errorMessage
		super().__init__(f"Error Code: {errorCode}, {errorMessage}")


FailedTapoRequestException = (TapoError, requests.exceptions.ConnectionError)
