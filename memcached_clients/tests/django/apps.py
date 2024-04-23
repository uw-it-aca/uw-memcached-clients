# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.apps import AppConfig


class MemcacheTestConfig(AppConfig):
    name = 'django_backend'
    path = 'memcached_clients/django_backend'
