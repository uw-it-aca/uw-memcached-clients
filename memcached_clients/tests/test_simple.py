from unittest import TestCase, skipUnless
from commonconf import settings, override_settings
from memcached_clients import SimpleClient
from pymemcache.exceptions import MemcacheError
import os


class SimpleCacheOfflineTests(TestCase):
    def setUp(self):
        self.client = SimpleClient()

    def test_invalid_method(self):
        self.assertRaises(AttributeError, self.client.fake)


@override_settings(MEMCACHED_SERVERS=[("localhost", "11211")],
                   MEMCACHED_NOREPLY=False)
@skipUnless(os.getenv("LIVE_TESTS"), "Set LIVE_TESTS=1 to run tests")
class SimpleCacheLiveTests(TestCase):
    @override_settings(MEMCACHED_SERVERS=[("localhost", "11211")])
    def setUp(self):
        self.client = SimpleClient()
        self.client.flush_all()

    def test_simple_set_get(self):
        key = "abc"

        reply = self.client.set(key, 12345)
        self.assertTrue(reply)
        self.assertEqual(self.client.get(key), 12345)

        reply = self.client.set(key, ["a", "b", "c"])
        self.assertTrue(reply)
        self.assertEqual(self.client.get(key), ["a", "b", "c"])
