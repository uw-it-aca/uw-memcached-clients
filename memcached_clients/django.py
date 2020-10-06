from django.core.cache.backends.memcached import BaseMemcachedCache
from pymemcache import HashClient
from pymemcache import serde


class PymemcacheCache(BaseMemcachedCache):
    """
    Implementation of a pymemcache binding for Django.
    """
    def __init__(self, server, params):
        self._local = local()
        super().__init__(server, params, library=pymemcache,
                         value_not_found_exception=KeyError)
        self._class = self._lib.HashClient
        self._options.update({
            "allow_unicode_keys": True,
            "default_noreply": False,
            "serde": serde.pickle_serde,
        })
