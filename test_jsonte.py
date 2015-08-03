#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_jsonte
----------------------------------

Tests for `jsonte` module.
"""

import datetime
import decimal
import json
import unittest

import dateutil.tz
from six import StringIO

import jsonte


class TestJsonte(unittest.TestCase):
    def setUp(self):
        self.serialiser = jsonte.JsonteSerialiser()

    def test_timestamp(self):
        now = datetime.datetime.now()
        self.assertEqual(now, self.serialiser.loads(self.serialiser.dumps(now)))

    def test_timestamp_with_timezone(self):
        now_with_timezone = datetime.datetime.now(dateutil.tz.gettz('Australia/Victoria'))
        self.assertEqual(now_with_timezone, self.serialiser.loads(self.serialiser.dumps(now_with_timezone)))

    def test_date(self):
        today = datetime.date.today()
        self.assertEqual(today, self.serialiser.loads(self.serialiser.dumps(today)))

    def test_time(self):
        time_now = datetime.datetime.now().time()
        self.assertEqual(time_now, self.serialiser.loads(self.serialiser.dumps(time_now)))

    def test_decimal(self):
        number = decimal.Decimal('324532.8437258')
        number2 = self.serialiser.loads(self.serialiser.dumps(number))
        self.assertEqual(number, number2)
        self.assertTrue(isinstance(number2, decimal.Decimal))

    def test_binary(self):
        binary = bytearray('Hello World!\x00\x01\x02', encoding='ascii')
        binary2 = self.serialiser.loads(self.serialiser.dumps(binary))
        self.assertEqual(binary, binary2)
        self.assertTrue(isinstance(binary2, bytearray))

    def test_escape_tilde(self):
        data = {u'~foo': u'bar'}
        jsonte_str = self.serialiser.dumps(data)
        print('jsonte_str: ' + jsonte_str)
        round_trip = self.serialiser.loads(jsonte_str)
        print(round_trip)
        via_json = json.loads(jsonte_str)
        self.assertEqual(data, round_trip)
        self.assertEqual(via_json, {u'~~foo': 'bar'})

    def test_hash_escape(self):
        data = {u'#foo': 'bar'}
        jsonte_str = self.serialiser.dumps(data)
        round_trip = self.serialiser.loads(jsonte_str)
        via_json = json.loads(jsonte_str)
        self.assertEqual(data, round_trip)
        self.assertEqual(via_json, {u'~#foo': u'bar'})

    def test_not_escaped(self):
        data = {u'*foo': u'bar'}
        via_json = json.loads(self.serialiser.dumps(data))
        self.assertEqual(via_json, data)

    def test_dump_and_load(self):
        data = {u'now': datetime.datetime.now(),
                u'number': decimal.Decimal('10.00'),
                u'#escape': u'test',
                u'~tilde_test': u'aaa',
                u'binary': bytearray(b'\x00\x01')
                }
        fp = StringIO()
        self.serialiser.dump(data, fp)
        fp.seek(0)
        round_trip = self.serialiser.load(fp)
        self.assertEqual(data, round_trip)
        fp.close()


class TestCustomEscape(unittest.TestCase):
    def setUp(self):
        self.serialiser = jsonte.JsonteSerialiser()
        self.serialiser.reserved_initial_chars += u'*'

    def test_custom_escape(self):
        data = {u'*foo': u'bar'}
        jsonte_str = self.serialiser.dumps(data)
        round_trip = self.serialiser.loads(jsonte_str)
        via_json = json.loads(jsonte_str)
        self.assertEqual(data, round_trip)
        self.assertEqual(via_json, {u'~*foo': u'bar'})


class TestNoEscape(unittest.TestCase):
    def setUp(self):
        self.serialiser = jsonte.JsonteSerialiser(escape_char=u'')

    def test_no_escape_simple(self):
        data = {u'#foo': u'bar'}
        jsonte_str = self.serialiser.dumps(data)
        round_trip = self.serialiser.loads(jsonte_str)
        via_json = json.loads(jsonte_str)
        self.assertEqual(data, round_trip)
        self.assertEqual(via_json, {u'#foo': u'bar'})

    def test_no_escape_complex(self):
        data = {u'now': datetime.datetime.now(),
                u'number': decimal.Decimal('10.00'),
                u'#escape': u'test',
                u'~tilde_test': u'aaa',
                u'binary': bytearray(b'\x00\x01')
                }
        jsonte_str = self.serialiser.dumps(data)
        round_trip = self.serialiser.loads(jsonte_str)
        self.assertEqual(data, round_trip)

    def test_round_trip_fail(self):
        data = {u'#num': u'aaa'}
        jsonte_str = self.serialiser.dumps(data)
        via_json = json.loads(jsonte_str)
        self.assertEqual(via_json, {u'#num': u'aaa'})
        with self.assertRaises(decimal.InvalidOperation):
            self.serialiser.loads(jsonte_str)


class TestWebsafety(unittest.TestCase):
    def test_raise_exception(self):
        serialiser = jsonte.JsonteSerialiser(array_websafety='exception')
        data = [u'a', u'list']
        with self.assertRaises(RuntimeError):
            serialiser.dumps(data)

    def test_prefix(self):
        serialiser = jsonte.JsonteSerialiser(array_websafety='prefix')
        data = [u'a', u'list']
        jsonte_str = serialiser.dumps(data)
        first_line = jsonte_str.splitlines()[0]
        self.assertEqual(first_line, u")]}',")


class TestCustomObjectHook(unittest.TestCase):
    def test_custom_objecthook(self):
        class Foo(object):
            pass

        def foo_hook(dct):
            if u'**foo**' in dct:
                return Foo()
            return None

        serialiser = jsonte.JsonteSerialiser(custom_objecthook=foo_hook)
        data = [{u'**foo**': 1}, {u'**bar**': 2}]
        raw_json = json.dumps(data)
        list_back = serialiser.loads(raw_json)
        self.assertIsInstance(list_back[0], Foo)
        self.assertEqual(list_back[1], {u'**bar**': 2})


class TestOrderIndependance(unittest.TestCase):
    def test_order_independance(self):
        class Foo(object):
            pass

        # noinspection PyUnusedLocal
        def foo_serialiser(foo_inst):
            dct = jsonte.SerialisationDict()
            dct[u'#foo'] = u'A foo instance'
            return dct

        # noinspection PyUnusedLocal
        def obj_serialiser(obj_inst):
            dct = jsonte.SerialisationDict()
            dct[u'#obj'] = u'A obj instance'
            return dct

        serialiser = jsonte.JsonteSerialiser()
        serialiser.add_type_serialiser(object, obj_serialiser)
        serialiser.add_type_serialiser(Foo, foo_serialiser)
        serialiser.finalise_serialisers()

        f = Foo()
        jsonte_str = serialiser.dumps(f)
        self.assertTrue(u'A foo instance' in jsonte_str)


if __name__ == '__main__':
    unittest.main()
