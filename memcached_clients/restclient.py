from memcached_clients import SimpleClient
from logging import getLogger
from datetime import datetime
import threading

logger = getLogger(__name__)


class CachedHTTPResponse():
    """
    Represents an HTTPResponse, implementing methods as needed.
    """
    def __init__(self, **kwargs):
        self.headers = kwargs.get("headers")
        self.status = kwargs.get("status")
        self.data = kwargs.get("data")

    def read(self):
        return self.data

    def getheader(self, field, default=''):
        if self.headers:
            for header in self.headers:
                if field.lower() == header.lower():
                    return self.headers[header]
        return default


class RestclientCacheClient(SimpleClient):
    def __init__(self):
        thread_id = threading.current_thread().ident
        if not hasattr(RestclientCacheClient, "_clients"):
            RestclientCacheClient._clients = {}

        if thread_id in RestclientCacheClient._clients:
            self.client = RestclientCacheClient._clients[thread_id]
        else:
            self.client = self._init_client()
            RestclientCacheClient._clients[thread_id] = self.client

    def getCache(self, service, url, headers):
        data = self.get(self._make_key(service, url))
        if data:
            return {"response": CachedHTTPResponse(**data)}

    def deleteCache(self, service, url):
        return self.delete(self._make_key(service, url))

    def updateCache(self, service, url, new_data, new_data_dt):
        data = self._make_cache_data(new_data, {}, 200, new_data_dt)
        self.replace(self._make_key(service, url), data, expire=expire)

    def processResponse(self, service, url, response):
        header_data = {}
        for header in response.headers:
            header_data[header] = response.getheader(header)

        data = self._make_cache_data(
            response.data, header_data, response.status, datetime.now())
        self.set(self._make_key(service, url), data, expire=expire)

    def _make_key(self, service, url):
        return "{}-{}".format(service, url)

    def _make_cache_data(self, data, headers, status, timestamp):
        return {
            "status": status,
            "headers": headers,
            "data": data,
            "time_stamp": timestamp.isoformat(),
        }
