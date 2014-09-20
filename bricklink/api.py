'''
    bricklink.api
    -------------

    A module providing access to the Bricklink API
'''

from .exceptions import *

from .methods import *

from base64 import b64encode
from hashlib import sha1
import hmac
import json
from random import getrandbits
from time import time
from urllib import quote, urlencode
import urllib2
from urlparse import urlparse

class ApiClient:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.trace_level = 0

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.catalog = Catalog(self)
        self.inventory = Inventory(self)
        self.orders = Orders(self)

    def trace(self, level, *args):
        if self.trace_level >= level:
            print('DEBUG: ' + ' '.join(str(arg) for arg in args))

    def normalizeURL(self, url):
        pu = urlparse(urlparse(url).geturl())
        url = "%s://%s%s%s" % (
            pu.scheme,
            pu.hostname,
            "" if not pu.port or {"http":80,"https":443}[pu.scheme] == pu.port else ":%d" % pu.port,
            pu.path,
        )
        return url

    def getSignature(self, absoluteURI, method, data):
        norm_url = self.normalizeURL(absoluteURI)
        norm_parameters = urlencode(sorted(data.items()))
        sig_base = '%s&%s&%s' % (method.upper(), quote(norm_url, ''), quote(norm_parameters, ''))
        key = '%s&%s' % (quote(self.consumer_secret.encode('utf-8'), ''), self.access_token_secret)
        signature = b64encode(hmac.new(key, sig_base, sha1).digest())
        self.trace(4, 'getSignature: data:', data)
        self.trace(4, 'getSignature: normalized:', norm_url)
        self.trace(4, 'getSignature: normalized parameters:', norm_parameters)
        self.trace(4, 'getSignature: base string:', sig_base)
        self.trace(4, 'getSignature: key:', key)
        self.trace(4, 'getSignature: signature:', signature)
        return signature

    def processResponse(self, response):
        if not 'meta' in response:
            raise BricklinkInvalidResponseException('No meta and/or data key in response')

        meta = response['meta']
        if meta['code'] not in (200, 201, 204):
            if meta['message'] == 'INVALID_URI': raise BricklinkInvalidURIException(meta['description'])
            elif meta['message'] == 'INVALID_REQUEST_BODY': raise BricklinkInvalidRequestBodyException(meta['description'])
            elif meta['message'] == 'PARAMETER_MISSING_OR_INVALID': raise BricklinkParameterMissingOrInvalidException(meta['description'])
            elif meta['message'] == 'BAD_OAUTH_REQUEST': raise BricklinkBadOauthRequestException(meta['description'])
            elif meta['message'] == 'PERMISSION_DENIED': raise BricklinkPermissionDeniedException(meta['description'])
            elif meta['message'] == 'RESOURCE_NOT_FOUND': raise BricklinkResourceNotFoundException(meta['description'])
            elif meta['message'] == 'METHOD_NOT_ALLOWED': raise BricklinkMethodNotAllowedException(meta['description'])
            elif meta['message'] == 'UNSUPPORTED_MEDIA_TYPE': raise BricklinkUnsupportedMediaTypeException(meta['description'])
            elif meta['message'] == 'RESOURCE_UPDATE_NOT_ALLOWED': raise BricklinkResourceUpdateNotAllowedException(meta['description'])
            elif meta['message'] == 'INTERNAL_SERVER_ERROR': raise BricklinkInternalServerErrorException(meta['description'])
            else: raise BricklinkUnspecifiedException(meta['code'], meta['message'], meta['description'])

        data = response['data']
        return data

    def request(self, method, relativeURI, params):
        # strip None values from params:
        #params = {k: v for k, v in params.items() if v is not None}

        if not relativeURI.startswith('/'):
            self.trace(4, 'request: added missing leading "/"')
            relativeURI = '/' + relativeURI
        absoluteURI = 'https://api.bricklink.com/api/store/v1' + relativeURI
        self.trace(4, 'request: absolute URI:', absoluteURI)

        oauth_params = dict()
        oauth_params['oauth_version'] = '1.0'
        oauth_params['oauth_consumer_key'] = self.consumer_key
        oauth_params['oauth_token'] = self.access_token
        oauth_params['oauth_timestamp'] = str(int(time()))
        oauth_params['oauth_nonce'] = b64encode('%0x' % getrandbits(256))[:32]
        oauth_params['oauth_signature_method'] = 'HMAC-SHA1'

        all_params = dict(oauth_params.items() + params.items())
        oauth_params['oauth_signature'] = self.getSignature(absoluteURI, method, all_params)

        kk = ["oauth_signature","oauth_nonce","oauth_version","oauth_consumer_key","oauth_signature_method","oauth_token","oauth_timestamp"]
        auth_str = 'Authorization={%s}' % '%2C'.join(['"%s"%%3A"%s"' % (k, quote(oauth_params[k], '')) for k in kk])

        full_url = absoluteURI + '?' + '&'.join(['%s=%s' % (k, quote(str(params[k]).encode('utf-8'), '')) for k in params.keys()] + [auth_str])
        self.trace(4, 'request: full URL:', full_url)

        f = urllib2.urlopen(full_url)
        response = json.loads(f.read())
        self.trace(4, 'request: response:', response)
        f.close()

        return self.processResponse(response)

    def get(self, relativeURI, params={}):
        return self.request('GET', relativeURI, params)

    def post(self, relativeURI, params={}):
        return self.request('POST', relativeURI, params)

    def put(self, relativeURI, params={}):
        return self.request('PUT', relativeURI, params)

    def delete(self, relativeURI, params={}):
        return self.request('DELETE', relativeURI, params)
