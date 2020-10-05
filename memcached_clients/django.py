from memcached_clients import SimpleClient
from django.core.cache.backends.memcached import BaseMemcachedCache


class SimpleCacheBackend(BaseMemcachedCache):
    """
    Implemetation of a memcached binding for Django.
    """
    def __init__(self, server, params):
        super().__init__(server, params, library=SimpleClient,
                         value_not_found_exception=ValueError)

    @cached_property
    def _cache(self):
        if getattr(self, '_client', None) is None:
            self._options["default_noreply"] = False
            self._client = SimpleClient(**self._options)
        return self._client

    def close(self, **kwargs):
        pass
