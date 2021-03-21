# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from memcached_clients import PymemcacheClient, RestclientPymemcacheClient


class TestPymemcacheClient(PymemcacheClient):
    @property
    def client(self):
        # Suppress thread-cached client
        return self.__client__()


class TestRestclientPymemcacheClient(RestclientPymemcacheClient):
    @property
    def client(self):
        # Suppress thread-cached client
        return self.__client__()
