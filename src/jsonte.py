
import base64
import decimal
import datetime
import json

import dateutil.parser

class JsonTypeRegister(object):
    def __init__(self):
        self._serialisers = []    # list of tuples ( Class , function that converts the object to a dict )
        self._deserialisers = []  # list of tuples ( #name , function that returns the object )
        self.default_func = None
        self.objecthook_func = None
    def add_serialiser(self, cls, obj_to_dict_func):
        '''
        :param cls: The class to serialise
        :param obj_to_dict_func: A function that turns an instance of the given class into a json serialisable dict

        NOTE: The order that classes are added is important, since the first serialiser found that the object
              is an instance of will be used.

              For example, a datetime.datetime instance is both a datetime.datetime, and a datetime.date, so for
              correct serialisation the serialiser for datetime.datetime must be added first.
        '''
        self._serialisers.append((cls, obj_to_dict_func))
    def add_deserialiser(self, name, dict_to_obj_func):
        self._deserialisers.append((name, dict_to_obj_func))
    def jsonte_default(self, obj):
        for cls, obj_to_dict_func in self._serialisers:
            if isinstance(obj, cls):
                return obj_to_dict_func(obj)
        if self.default_func:
            return self.default_func(obj)
        raise TypeError(repr(obj) + " is not Json serialisable")
    def jsonte_objecthook(self, dct):
        assert isinstance(dct, dict)
        for keyname, dict_to_obj_func in self._deserialisers:
            if keyname in dct.keys():
                return dict_to_obj_func(dct)
        if self.objecthook_func:
            return self.objecthook_func(dct)
        else:
            return dct

json_type_register = JsonTypeRegister()

# numeric ( python decimal.Decimal )
json_type_register.add_serialiser(decimal.Decimal, lambda decimal: {'#num': str(decimal)})
json_type_register.add_deserialiser('#num', lambda dct: decimal.Decimal(dct['#num']))

# timestamp ( python datetime.datetime )
json_type_register.add_serialiser(datetime.datetime, lambda tstamp: {'#tstamp': tstamp.isoformat() })
json_type_register.add_deserialiser('#tstamp', lambda dct: dateutil.parser.parse(dct['#tstamp']))

# date
json_type_register.add_serialiser(datetime.date, lambda dte: {'#date': dte.isoformat() })
json_type_register.add_deserialiser('#date', lambda dct: datetime.datetime.strptime(dct['#date'], '%Y-%m-%d').date())

# time
json_type_register.add_serialiser(datetime.time, lambda t: {'#time': t.isoformat() })
json_type_register.add_deserialiser('#time', lambda dct: dateutil.parser.parse(dct['#time']).time())

# binary  ( python bytearray - 2.6 and higher )
json_type_register.add_serialiser(bytearray, lambda bin: {'#bin': base64.b64encode(bin) })
json_type_register.add_deserialiser('#bin', lambda dct: bytearray(base64.b64decode(dct['#bin'])))


# ---------------------------------

def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        encoding='utf-8', sort_keys=False, **kw):
    return json.dumps(obj, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
        allow_nan=allow_nan, cls=cls, indent=indent, separators=separators,
        encoding=encoding, default=json_type_register.jsonte_default, sort_keys=sort_keys, **kw)

def loads(s, encoding=None, cls=None, parse_float=None, parse_int=None, parse_constant=None, **kw):
    return json.loads(s, encoding=encoding, cls=cls, object_hook=json_type_register.jsonte_objecthook,
                      parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, **kw)

# ----------------------------------

def test():
    from pprint import pprint
    d = dict(cost=decimal.Decimal('10.0200'),
             discounted=True,
             now=datetime.datetime.now(),
             now_with_tz = datetime.datetime.now(dateutil.tz.gettz('Australia/Victoria')),
             today = datetime.date.today(),
             binary = bytearray('Hello World!\x00\x01\x02')
             )
    s = dumps(d)
    print s

    d2 = loads(s)
    pprint(d2)

    print 'd == d2:', d == d2

if __name__=='__main__':
    test()
