from pymemcache.exceptions import MemcacheError
from pymemcache.client.hash import HashClient
from pymemcache import serde
from commonconf import settings
from logging import getLogger
import threading

logger = getLogger(__name__)


class SimpleClient():
    """
    A settings-based wrapper around pymemcache.
    """
    def __init__(self, **kwargs):
        self.client = self._init_client(**kwargs)

    def __getattr__(self, name, *args, **kwargs):
        """
        Pass method calls through to the client, and add logging for errors.
        """
        def handler(*args, **kwargs):
            try:
                return getattr(self.client, name)(*args, **kwargs)
            except MemcacheError as ex:
                logger.error("memcached {}: {}".format(name, ex))
            except AttributeError:
                raise
        return handler

    def _init_client(self, **kwargs):
        default_noreply = kwargs.get("default_noreply")
        if default_noreply is None:
            default_noreply = getattr(settings, "MEMCACHED_NOREPLY", True)

        return HashClient(
            getattr(settings, "MEMCACHED_SERVERS", []),
            use_pooling=True,
            max_pool_size=getattr(settings, "MEMCACHED_MAX_POOL_SIZE", 10),
            connect_timeout=getattr(settings, "MEMCACHED_CONNECT_TIMEOUT", 2),
            timeout=getattr(settings, "MEMCACHED_TIMEOUT", 2),
            default_noreply=default_noreply,
            serde=serde.pickle_serde)
