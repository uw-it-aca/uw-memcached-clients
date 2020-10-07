from django.core.cache.backends.memcached import BaseMemcachedCache
from pymemcache import HashClient
from pymemcache import serde


class PymemcacheCache(BaseMemcachedCache):
    """
    Implementation of a pymemcache binding for Django.
    """
    def __init__(self, server, params):
        super().__init__(server, params, library=pymemcache,
                         value_not_found_exception=KeyError)
        self._class = self._lib.HashClient
        self._options.update({
            "allow_unicode_keys": True,
            "default_noreply": False,
            "serde": serde.pickle_serde,
        })

    def close(self, **kwargs):
        # Don't call disconnect_all() if connection pooling is enabled,
        # as it resets the failover state and creates unnecessary reconnects.
        if not self._cache.use_pooling:
            self._cache.disconnect_all()
