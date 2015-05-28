#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_jsonte
----------------------------------

Tests for `jsonte` module.
"""

import datetime
import decimal
import tempfile
import unittest

import dateutil.tz

import json
import jsonte

class TestJsonte(unittest.TestCase):

    def test_timestamp(self):
        now = datetime.datetime.now()
        self.assertEqual(now, jsonte.loads(jsonte.dumps(now)))

    def test_timestamp_with_timezone(self):
        now_with_timezone = datetime.datetime.now(dateutil.tz.gettz('Australia/Victoria'))
        self.assertEqual(now_with_timezone, jsonte.loads(jsonte.dumps(now_with_timezone)))

    def test_date(self):
        today = datetime.date.today()
        self.assertEqual(today, jsonte.loads(jsonte.dumps(today)))

    def test_time(self):
        time_now = datetime.datetime.now().time()
        self.assertEqual(time_now, jsonte.loads(jsonte.dumps(time_now)))

    def test_decimal(self):
        number = decimal.Decimal('324532.8437258')
        number2 = jsonte.loads(jsonte.dumps(number))
        self.assertEqual(number, number2)
        self.assertTrue(isinstance(number2, decimal.Decimal))

    def test_binary(self):
        binary = bytearray('Hello World!\x00\x01\x02')
        binary2 = jsonte.loads(jsonte.dumps(binary))
        self.assertEqual(binary, binary2)
        self.assertTrue(isinstance(binary2, bytearray))

    def test_escape_tilde(self):
        data = {'~foo': 'bar'}
        jsonte_str = jsonte.dumps(data)
        round_trip = jsonte.loads(jsonte_str)
        via_json = json.loads(jsonte_str)
        self.assertEqual(data, round_trip)
        self.assertEqual(via_json, {'~~foo': 'bar'})

    def test_hash_escape(self):
        data = {'#foo': 'bar'}
        jsonte_str = jsonte.dumps(data)
        round_trip = jsonte.loads(jsonte_str)
        via_json = json.loads(jsonte_str)
        self.assertEqual(data, round_trip)
        self.assertEqual(via_json, {'~#foo': 'bar'})

    def test_not_escaped(self):
        data = {'*foo': 'bar'}
        via_json = json.loads(jsonte.dumps(data))
        self.assertEqual(via_json, data)

    def test_dump_and_load(self):
        data = { 'now': datetime.datetime.now(),
                 'number': decimal.Decimal('10.00'),
                 '#escape': 'test',
                 '~tilde_test': 'aaa',
                 'binary': bytearray('\x00\x01')
                  }
        with tempfile.TemporaryFile() as fp:
            jsonte.dump(data, fp)
            fp.seek(0)
            round_trip = jsonte.load(fp)
            self.assertEqual(data, round_trip)

class TestCustomEscape(unittest.TestCase):

    def setUp(self):
        self.current_reserved = jsonte.jsonte_type_register.reserved_initial_chars
        jsonte.jsonte_type_register.reserved_initial_chars += '*'

    def test_custom_escape(self):
        data = {'*foo': 'bar'}
        jsonte_str = jsonte.dumps(data)
        round_trip = jsonte.loads(jsonte_str)
        via_json = json.loads(jsonte_str)
        self.assertEqual(data, round_trip)
        self.assertEqual(via_json, {'~*foo': 'bar'})

    def tearDown(self):
        jsonte.jsonte_type_register.reserved_initial_chars = self.current_reserved

if __name__ == '__main__':
    unittest.main()
