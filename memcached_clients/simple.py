from pymemcache.client.hash import HashClient
from pymemcache import serde
from commonconf import settings
from logging import getLogger
import threading

logger = getLogger(__name__)


class SimpleClient():
    def __init__(self):
        thread_id = threading.current_thread().ident
        if not hasattr(MemcachedClient, "_clients"):
            MemcachedClient._clients = {}

        if thread_id in MemcachedClient._clients:
            self.client = MemcachedClient._clients[thread_id]
        else:
            self.client = self._client()
            MemcachedClient._clients[thread_id] = self.client

    def get(self, key):
        try:
            return self.client.get(key)
        except Exception as ex:
            logger.error("CACHE GET: {}".format(ex))

    def set(self, key, data, expire=0):
        try:
            self.client.set(key, data, expire=expire)
        except Exception as ex:
            logger.error("CACHE SET: {}".format(ex))

    def replace(self, key, data, expire=0):
        try:
            self.client.replace(key, data, expire=expire)
        except Exception as ex:
            logger.error("CACHE REPLACE: {}".format(ex))

    def delete(self, key):
        try:
            return self.client.delete(key)
        except Exception as ex:
            logger.error("CACHE DELETE: {}".format(ex))

    def _init_client(self):
        return HashClient(
            getattr(settings, "RESTCLIENTS_MEMCACHED_SERVERS", []),
            use_pooling=True,
            max_pool_size=getattr(settings, "MEMCACHED_MAX_POOL_SIZE", 10),
            connect_timeout=getattr(settings, "MEMCACHED_CONNECT_TIMEOUT", 2),
            timeout=getattr(settings, "MEMCACHED_TIMEOUT", 2),
            serde=serde.pickle_serde)
