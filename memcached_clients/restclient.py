from memcached_clients import SimpleClient
from commonconf import settings
from importlib import import_module
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


class CachePolicy():
    def get_cache_expiration_time(self, service, url):
        return 0


class RestclientCacheClient(SimpleClient):
    def __init__(self):
        policy_class = getattr(settings, "RESTCLIENTS_CACHE_POLICY_CLASS")
        if policy_class:
            self.policy = self._init_policy(policy_class)
        else:
            self.policy = CachePolicy()

        thread_id = threading.current_thread().ident
        if not hasattr(RestclientCacheClient, "_clients"):
            RestclientCacheClient._clients = {}

        if thread_id in RestclientCacheClient._clients:
            self.client = RestclientCacheClient._clients[thread_id]
        else:
            self.client = self._init_client()
            RestclientCacheClient._clients[thread_id] = self.client

    def getCache(self, service, url, headers):
        expire = self.policy.get_cache_expiration_time(service, url)
        if expire is not None:
            data = self.get(self._make_key(service, url))
            if data:
                return {"response": CachedHTTPResponse(**data)}

    def deleteCache(self, service, url):
        return self.delete(self._make_key(service, url))

    def updateCache(self, service, url, new_data, new_data_dt):
        expire = self.policy.get_cache_expiration_time(service, url)
        if expire is not None:
            data = self._make_cache_data(new_data, {}, 200, new_data_dt)
            self.replace(self._make_key(service, url), data, expire=expire)

    def processResponse(self, service, url, response):
        expire = self.policy.get_cache_expiration_time(service, url)
        if expire is not None:
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

    def _init_policy(self, dotted_path):
        try:
            module_path, class_name = dotted_path.rsplit('.', 1)
        except ValueError:
            raise ImportError("Not a module path: {}".format(dotted_path))

        module = import_module(module)

        try:
            return getattr(module, class_name)
        except AttributeError:
            raise ImportError("Module {} does not define {}".format(
                module_path, class_name))
