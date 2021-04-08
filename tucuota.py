import requests
import logging

import hmac
import hashlib
import base64
import json

import time
from hashlib import sha256

class TuCuotaException(Exception):
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return self.value

class TuCuotaRequestFailed(TuCuotaException):
	pass

class TuCuotaSignatureVerificationError(TuCuotaException):
	pass


class Webhook(object):
	DEFAULT_TOLERANCE = 300

	@staticmethod
	def construct_event(
		payload, timestamp, received_sig, secret, tolerance=DEFAULT_TOLERANCE
	):
		if hasattr(payload, "decode"):
			payload = payload.decode("utf-8")

		WebhookSignature.check(payload, timestamp, received_sig, secret, tolerance)

		data = json.loads(payload)

		return data


class WebhookSignature(object):
	EXPECTED_SCHEME = "v1"

	@staticmethod
	def _compute_signature(payload, secret):
		mac = hmac.new(
			secret.encode("utf-8"),
			msg=payload.encode("utf-8"),
			digestmod=sha256,
		)
		return mac.hexdigest()


	@classmethod
	def check(cls, payload, timestamp, received_sig, secret, tolerance=None):
		signatures = received_sig.split(' ')
		signed_payload = "%s%s" % (payload,timestamp)
		expected_sig = cls._compute_signature(signed_payload, secret)
		if not any(expected_sig == s for s in signatures):
			raise TuCuotaSignatureVerificationError(
				"No signatures found matching the expected signature for "
			)

		if tolerance and int(timestamp) < time.time() - tolerance:
			raise TuCuotaSignatureVerificationError(
				"Timestamp outside the tolerance zone (%d)" % timestamp,
			)

		return True


class TC(object):
	sandbox = False
	local = False
	token = None

	def __init__(self, token):
		self.token = token

	def baseUri(self):
		return 'https://sandbox.tucuota.com/' if self.sandbox else 'https://tucuota.com/'

	def headers(self):
		return {
			"Authorization":"Bearer " + self.token,
			"Content-Type": "application/json",
			"Accept": "application/json",
		}

	def handleRequest(self, request):
		if request.status_code in [401, 403]:
			raise TuCuotaRequestFailed("Unauthenticated. Verify token and environment")

		if request.status_code < 202:
			return {
				"status": request.status_code,
				"data": request.json().get('data'),
				"meta": request.json().get('meta'),
			}

		# if request.status_code < 500:
		#     return {
		#         "status": request.status_code,
		#         "message": request.json().get('message'),
		#         "errors": request.json().get('errors')
		#     }

		else:
			raise TuCuotaRequestFailed("%s: %s %s" % (request.status_code, request.json().get('message'), request.json().get('errors') ))


	def get(self, uri, params=None):
		"""
		Generic resource get
		@param uri
		@param params = None
		@return json

		"""
		if params is None:
			params = {}

		request = requests.get(self.baseUri() + uri, params, headers=self.headers(), allow_redirects=False)
		return self.handleRequest(request);


	def post(self, uri, data, params=None):
		"""
		Generic resource post
		@param uri
		@param data
		@param params = None
		@return json

		"""
		if params is None:
			params = {}

		request = requests.post(self.baseUri() + uri,  params, data, headers=self.headers(), allow_redirects=False)
		return self.handleRequest(request);

	def put(self, uri, data, params=None):
		"""
		Generic resource put
		@param uri
		@param data
		@param params = None
		@return json

		"""
		if params is None:
			params = {}

		request = requests.put(self.baseUri() + uri, params, data, headers=self.headers(), allow_redirects=False)
		return self.handleRequest(request);

	def patch(self, uri, data, params=None):
		"""
		Generic resource patch
		@param uri
		@param data
		@param params = None
		@return json

		"""
		if params is None:
			params = {}

		request = requests.patch(self.baseUri() + uri, params, data, headers=self.headers(), allow_redirects=False)
		return self.handleRequest(request);

	def delete(self, uri, params=None):
		"""
		Generic resource delete
		@param uri
		@param params = None
		@return json

		"""
		if params is None:
			params = {}

		request = requests.delete(self.baseUri() + uri, params, headers=self.headers(), allow_redirects=False)
		return self.handleRequest(request);