# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from memcached_clients import PymemcacheClient
from commonconf import settings
from hashlib import sha1
from logging import getLogger

logger = getLogger(__name__)


class CachedHTTPResponse():
    """
    Represents an HTTPResponse, implementing methods as needed.
    """
    def __init__(self, **kwargs):
        self.headers = kwargs.get("headers", {})
        self.status = kwargs.get("status")
        self.data = kwargs.get("data")

    def read(self):
        return self.data

    def getheader(self, val, default=''):
        for header in self.headers:
            if val.lower() == header.lower():
                return self.headers[header]
        return default


class RestclientPymemcacheClient(PymemcacheClient):
    def getCache(self, service, url, headers=None):
        expire = self.get_cache_expiration_time(service, url)
        if expire is not None:
            key = self._create_key(service, url)
            try:
                # Bypass the shim client to log the original URL if needed.
                data = self.client.get(key)
                if data:
                    return {"response": CachedHTTPResponse(**data)}
            except Exception as ex:
                logger.error(f"memcached get '{url}': {ex}")

    def deleteCache(self, service, url):
        return self.delete(self._create_key(service, url))

    def updateCache(self, service, url, response):
        expire = self.get_cache_expiration_time(service, url, response.status)
        if expire is not None:
            key = self._create_key(service, url)
            data = self._format_data(response)
            try:
                # Bypass the shim client to log the original URL if needed.
                self.client.set(key, data, expire=expire)
            except Exception as ex:
                logger.error(f"memcached set '{url}': {ex}")

    processResponse = updateCache

    def get_cache_expiration_time(self, service, url, status=None):
        """
        Overridable method for setting the cache expiration per service, url,
        and response status.  Valid return values are:
          * Number of seconds until the item is expired from the cache,
          * Zero, for no expiry,
          * None, indicating that the item should not be cached.
        """
        return getattr(settings, "RESTCLIENTS_MEMCACHED_DEFAULT_EXPIRY", 300)

    @staticmethod
    def _create_key(service, url):
        url_key = sha1(url.encode("utf-8")).hexdigest()
        return "{}-{}".format(service, url_key)

    @staticmethod
    def _format_data(response):
        # This step is needed because HTTPHeaderDict isn't serializable
        headers = {}
        if response.headers is not None:
            for header in response.headers:
                headers[header] = response.getheader(header)

        return {
            "status": response.status,
            "headers": headers,
            "data": response.data
        }
