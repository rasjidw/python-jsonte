
# standard libs
import base64
import decimal
import datetime
import json

# 3rd party
import dateutil.parser

# ours
from jsonte.core import JsonteDict, JsonteEncoder, JsonteTypeRegister


jsonte_type_register = JsonteTypeRegister()

# numeric ( python decimal.Decimal )
def decimal_serialiser(num):
    dct = JsonteDict()
    dct['#num'] = str(num)
    return dct

jsonte_type_register.add_serialiser(decimal.Decimal, decimal_serialiser)

def decimal_deserialiser(dct):
    value = decimal.Decimal(dct.pop('#num'))
    if dct: raise ValueError('Invalid #num')  # should be an empty dct
    return value

jsonte_type_register.add_deserialiser('#num', decimal_deserialiser)


# timestamp ( python datetime.datetime )
def timestamp_serialiser(tstamp):
    dct = JsonteDict()
    dct['#tstamp'] = tstamp.isoformat()
    return dct

jsonte_type_register.add_serialiser(datetime.datetime, timestamp_serialiser)

def timestamp_deserialiser(dct):
    value = dateutil.parser.parse(dct.pop('#tstamp'))
    if dct: raise ValueError('Invalid #tstamp')  # should be an empty dct
    return value

jsonte_type_register.add_deserialiser('#tstamp', timestamp_deserialiser)


# date
def date_serialiser(dte):
    dct = JsonteDict()
    dct['#date'] = dte.isoformat()
    return dct

jsonte_type_register.add_serialiser(datetime.date, date_serialiser)

def date_deserialiser(dct):
    value = datetime.datetime.strptime(dct.pop('#date'), '%Y-%m-%d').date()
    if dct: raise ValueError('Invalid #date')  # should be an empty dct
    return value

jsonte_type_register.add_deserialiser('#date', date_deserialiser)


# time
def time_serialiser(the_time):
    dct = JsonteDict()
    dct['#time'] = the_time.isoformat()
    return dct

jsonte_type_register.add_serialiser(datetime.time, time_serialiser)

def time_deserialiser(dct):
    value = dateutil.parser.parse(dct.pop('#time')).time()
    if dct: raise ValueError('Invalid #time')  # should be an empty dct
    return value

jsonte_type_register.add_deserialiser('#time', time_deserialiser)


# binary  ( python bytearray - 2.6 and higher )
def binary_serialiser(bin):
    dct = JsonteDict()
    dct['#bin'] = base64.b64encode(bin)
    return dct

jsonte_type_register.add_serialiser(bytearray, binary_serialiser)

def binary_deserialiser(dct):
    value = bytearray(base64.b64decode(dct.pop('#bin')))
    if dct: raise ValueError('Invalid #bin')  # should be an empty dct
    return value

jsonte_type_register.add_deserialiser('#bin', binary_deserialiser)



# ---------------------------------

def dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        encoding='utf-8', sort_keys=False, **kw):
    return JsonteEncoder(jsonte_type_register, skipkeys=skipkeys, ensure_ascii=ensure_ascii,
                         check_circular=check_circular, allow_nan=allow_nan, indent=indent,
                         separators=separators, encoding=encoding, sort_keys=sort_keys).encode(obj)

def loads(s, encoding=None, cls=None, parse_float=None, parse_int=None, parse_constant=None, **kw):
    return json.loads(s, encoding=encoding, cls=cls, object_hook=jsonte_type_register._jsonte_objecthook,
                      parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, **kw)



