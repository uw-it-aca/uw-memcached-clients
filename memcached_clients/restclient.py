from memcached_clients import SimpleClient
from commonconf import settings
from importlib import import_module
from logging import getLogger
from hashlib import sha1
import threading

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


class CachePolicy():
    def get_cache_expiry(self, service, url):
        """
        Overridable method for setting the cache expiry per service and url.
        Valid return values are:
          * Number of seconds until the item is expired from the cache,
          * Zero, for no expiry (the default),
          * None, indicating that the item should not be cached.
        """
        return 0


class RestclientCacheClient(SimpleClient):
    policy = None
    _clients = {}

    def __init__(self):
        if RestclientCacheClient.policy is None:
            policy_class = getattr(settings, "RESTCLIENTS_CACHE_POLICY_CLASS",
                                   "memcached_clients.restclient.CachePolicy")
            RestclientCacheClient.policy = self._get_policy(policy_class)

        thread_id = threading.current_thread().ident
        if thread_id in RestclientCacheClient._clients:
            self.client = RestclientCacheClient._clients[thread_id]
        else:
            self.client = self._init_client()
            RestclientCacheClient._clients[thread_id] = self.client

    def getCache(self, service, url, headers=None):
        expire = self.policy.get_cache_expiry(service, url)
        if expire is not None:
            data = self.get(self._create_key(service, url))
            if data:
                return {"response": CachedHTTPResponse(**data)}

    def deleteCache(self, service, url):
        return self.delete(self._create_key(service, url))

    def updateCache(self, service, url, response):
        expire = self.policy.get_cache_expiry(service, url)
        if expire is not None:
            key = self._create_key(service, url)
            data = self._format_data(response)
            return self.set(key, data, expire=expire)

    processResponse = updateCache

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

    @staticmethod
    def _get_policy(dotted_path):
        try:
            module_path, class_name = dotted_path.rsplit('.', 1)
        except (AttributeError, ValueError):
            raise ImportError("Not a module path: {}".format(dotted_path))

        module = import_module(module_path)

        try:
            return getattr(module, class_name)()
        except AttributeError:
            raise ImportError("Module {} does not define {}".format(
                module_path, class_name))
