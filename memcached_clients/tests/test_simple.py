from unittest import TestCase, skipIf
from commonconf import settings, override_settings
from memcached_clients import SimpleClient
from pymemcache.exceptions import MemcacheError


class SimpleCacheOfflineTests(TestCase):
    def setUp(self):
        self.client = SimpleClient()

    def test_valid_method(self):
        self.assertRaises(MemcacheError, self.client.get, "key")

    def test_invalid_method(self):
        self.assertRaises(AttributeError, self.client.fake)


@skipIf(not getattr(settings, "MEMCACHED_SERVERS"), "Memcached not configured")
@override_settings()
class SimpleCacheTests(TestCase):
    @override_settings(MEMCACHED_SERVERS=[("localhost", "11211")])
    def setUp(self):
        self.client = SimpleClient()
        self.client.client.flush_all()
