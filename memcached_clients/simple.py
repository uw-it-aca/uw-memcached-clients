from pymemcache.exceptions import MemcacheError
from pymemcache.client.hash import HashClient
from pymemcache import serde
from commonconf import settings
from logging import getLogger
import threading

logger = getLogger(__name__)


class SimpleClient():
    def __init__(self):
        thread_id = threading.current_thread().ident
        if not hasattr(SimpleClient, "_clients"):
            SimpleClient._clients = {}

        if thread_id in SimpleClient._clients:
            self.client = SimpleClient._clients[thread_id]
        else:
            self.client = self._init_client()
            SimpleClient._clients[thread_id] = self.client

    def __getattr__(self, name, *args, **kwargs):
        """
        Pass method calls through to the client.
        """
        def handler(*args, **kwargs):
            try:
                return getattr(self.client, name)(*args, **kwargs)
            except MemcacheError as ex:
                logger.error("CACHE {}: {}".format(name, ex))
            except AttributeError:
                raise
        return handler

    def _init_client(self):
        return HashClient(
            getattr(settings, "MEMCACHED_SERVERS", []),
            use_pooling=True,
            max_pool_size=getattr(settings, "MEMCACHED_MAX_POOL_SIZE", 10),
            connect_timeout=getattr(settings, "MEMCACHED_CONNECT_TIMEOUT", 2),
            timeout=getattr(settings, "MEMCACHED_TIMEOUT", 2),
            serde=serde.pickle_serde)
