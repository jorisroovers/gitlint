# -*- coding: utf-8 -*-
from gitlint.tests.base import BaseTestCase
from gitlint.cache import PropertyCache, cache


class CacheTests(BaseTestCase):

    class MyClass(PropertyCache):
        """ Simple class that has cached properties, used for testing. """

        def __init__(self):
            PropertyCache.__init__(self)
            self.counter = 0

        @property
        @cache
        def foo(self):
            self.counter += 1
            return "bår"

        @property
        @cache(cachekey="hür")
        def bar(self):
            self.counter += 1
            return "fōo"

    def test_cache(self):
        # Init new class with cached properties
        myclass = self.MyClass()
        self.assertEqual(myclass.counter, 0)
        self.assertDictEqual(myclass._cache, {})

        # Assert that function is called on first access, cache is set
        self.assertEqual(myclass.foo, "bår")
        self.assertEqual(myclass.counter, 1)
        self.assertDictEqual(myclass._cache, {"foo": "bår"})

        # After function is not called on subsequent access, cache is still set
        self.assertEqual(myclass.foo, "bår")
        self.assertEqual(myclass.counter, 1)
        self.assertDictEqual(myclass._cache, {"foo": "bår"})

    def test_cache_custom_key(self):
        # Init new class with cached properties
        myclass = self.MyClass()
        self.assertEqual(myclass.counter, 0)
        self.assertDictEqual(myclass._cache, {})

        # Assert that function is called on first access, cache is set with custom key
        self.assertEqual(myclass.bar, "fōo")
        self.assertEqual(myclass.counter, 1)
        self.assertDictEqual(myclass._cache, {"hür": "fōo"})

        # After function is not called on subsequent access, cache is still set
        self.assertEqual(myclass.bar, "fōo")
        self.assertEqual(myclass.counter, 1)
        self.assertDictEqual(myclass._cache, {"hür": "fōo"})
