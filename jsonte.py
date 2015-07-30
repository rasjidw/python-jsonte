# standard libs
import base64
import decimal
import datetime
import json

# 3rd party
import dateutil.parser

__all__ = ['PreEscapedKeysMixin', 'SerialisationDict', 'JsonteSerialiser']


class PreEscapedKeysMixin(object):
    pass


class SerialisationDict(dict, PreEscapedKeysMixin):
    pass


class JsonteSerialiser(object):
    def __init__(self, reserved_initial_chars='#', escape_char='~', array_websafety=None,
                 skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True,
                 indent=None, separators=None, encoding='utf-8', sort_keys=False):
        self.reserved_initial_chars = reserved_initial_chars
        self.escape_char = escape_char
        if array_websafety and array_websafety not in ('exception', 'prefix'):
            raise ValueError("array_websafety must be blank, 'exception' or 'prefix'")
        self.array_websafety = array_websafety
        self.websafety_prefix = ")]}',\n"  # prefix used by AngularJS - https://docs.angularjs.org/api/ng/service/$http

        self.skipkeys = skipkeys
        self.ensure_ascii = ensure_ascii
        self.check_circular = check_circular
        self.allow_nan = allow_nan
        self.indent = indent
        self.separators = separators
        self.encoding = encoding
        self.sort_keys = sort_keys

        self._serialisers = list()  # list of tuples ( Class , function that converts the object to a dict )
        self._deserialisers = list()  # list of tuples ( #name , function that returns the object )
        self._names = set()
        self._type_classes = set()
        self._add_standard_types()

    def get_type_classes(self):
        return self._type_classes

    def add_type_serialiser(self, obj_cls, obj_to_jsontedict_func):
        """
        :param obj_cls: The class to serialise
        :param obj_to_jsontedict_func: A function that turns an instance of the given class into a jsonte dict

        NOTE: The order that classes are added is important, since the first serialiser found that the object
              is an instance of will be used.

              For example, a datetime.datetime instance is both a datetime.datetime, and a datetime.date, so for
              correct serialisation the serialiser for datetime.datetime must be added first.
        """

        # FIXME: We can probably lift the requirement on ordering by using a digraph / partial order sort
        # See https://pypi.python.org/pypi/digraphtools for one possible option?

        if obj_cls in self._type_classes:
            raise ValueError('class %s already added' % obj_cls.__name__)
        self._type_classes.add(obj_cls)
        self._serialisers.append((obj_cls, obj_to_jsontedict_func))

    def add_type_deserialiser(self, name, dict_to_obj_func):
        if not name:
            raise ValueError('name must be at least one char long')
        if name[0] not in self.reserved_initial_chars:
            raise ValueError('name must start with a reserved char')
        if len(name) >= 2 and name[1] == self.escape_char:
            raise ValueError('the 2nd char of the name must not be the escape char')
        if name in self._names:
            raise ValueError('name %s already added' % name)
        self._names.add(name)
        self._deserialisers.append((name, dict_to_obj_func))

    def _jsonte_objecthook(self, dct):
        assert isinstance(dct, dict)
        for keyname, dict_to_obj_func in self._deserialisers:
            if keyname in dct:
                return dict_to_obj_func(dct)
        if self.escape_char:
            for key in dct.keys():   # don't iterate - must use .keys() here, since we are modifying the keys in place
                if key[0] == self.escape_char:
                    dct[key[1:]] = dct.pop(key)
        return dct
    
    def _add_standard_types(self):
        self.add_type_serialiser(decimal.Decimal, decimal_serialiser)
        self.add_type_deserialiser('#num', decimal_deserialiser)
        self.add_type_serialiser(datetime.datetime, timestamp_serialiser)
        self.add_type_deserialiser('#tstamp', timestamp_deserialiser)
        self.add_type_serialiser(datetime.date, date_serialiser)
        self.add_type_deserialiser('#date', date_deserialiser)
        self.add_type_serialiser(datetime.time, time_serialiser)
        self.add_type_deserialiser('#time', time_deserialiser)
        self.add_type_serialiser(bytearray, binary_serialiser)
        self.add_type_deserialiser('#bin', binary_deserialiser)

    def dump(self, obj, fp):
        if self.array_websafety and isinstance(obj, list):
            if self.array_websafety == 'exception':
                raise RuntimeError('passed a list with array_websafety set to exception')
            elif self.array_websafety == 'prefix':
                fp.write(self.websafety_prefix)
            else:
                raise RuntimeError('invalid array_websafety value')
        iterable = _JsonteEncoder(self, skipkeys=self.skipkeys, ensure_ascii=self.ensure_ascii,
                                  check_circular=self.check_circular, allow_nan=self.allow_nan, indent=self.indent,
                                  separators=self.separators, encoding=self.encoding,
                                  sort_keys=self.sort_keys).iterencode(obj)
        for chunk in iterable:
            fp.write(chunk)

    def dumps(self, obj):
        raw_json_str = _JsonteEncoder(self, skipkeys=self.skipkeys, ensure_ascii=self.ensure_ascii,
                                      check_circular=self.check_circular, allow_nan=self.allow_nan, indent=self.indent,
                                      separators=self.separators, encoding=self.encoding,
                                      sort_keys=self.sort_keys).encode(obj)
        if self.array_websafety and isinstance(obj, list):
            if self.array_websafety == 'exception':
                raise RuntimeError('passed a list with array_websafety set to exception')
            elif self.array_websafety == 'prefix':
                return self.websafety_prefix + raw_json_str
            else:
                raise RuntimeError('invalid array_websafety value')
        else:
            return raw_json_str

    def load(self, fp, encoding=None, cls=None, parse_float=None, parse_int=None, parse_constant=None, **kw):
        return json.load(fp, encoding=encoding, cls=cls, object_hook=self._jsonte_objecthook,
                         parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, **kw)

    def loads(self, s, encoding=None, cls=None, parse_float=None, parse_int=None, parse_constant=None, **kw):
        return json.loads(s, encoding=encoding, cls=cls, object_hook=self._jsonte_objecthook,
                          parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, **kw)


class _JsonteEncoder(json.JSONEncoder):
    def __init__(self, jsonte_serialiser, skipkeys=False, ensure_ascii=True,
                 check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, encoding='utf-8'):
        assert isinstance(jsonte_serialiser, JsonteSerialiser)
        self.jsonte_serialiser = jsonte_serialiser
        self.chars_to_escape = self.jsonte_serialiser.reserved_initial_chars + self.jsonte_serialiser.escape_char
        self.escape_char = self.jsonte_serialiser.escape_char
        # noinspection PyProtectedMember
        self.jsonte_type_serialisers = self.jsonte_serialiser._serialisers
        json.JSONEncoder.__init__(self, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                                  allow_nan=allow_nan, sort_keys=sort_keys, indent=indent, separators=separators,
                                  encoding=encoding)

    def default(self, obj):
        for cls, obj_to_jsontedict_func in self.jsonte_type_serialisers:
            if isinstance(obj, cls):
                value = obj_to_jsontedict_func(obj)
                if not isinstance(value, PreEscapedKeysMixin) or not isinstance(value, dict):
                    raise TypeError('serialisers must return subclass of both dict and PreEscapedKeysMixin')
                return value
        return json.JSONEncoder.default(self, obj)

    def iterencode(self, obj, _one_shot=False):
        if isinstance(obj, dict) and not isinstance(obj, PreEscapedKeysMixin) and self.jsonte_serialiser.escape_char:
            # prefix any keys starting with something in reserved_initial_chars with the escape char
            keys_to_escape = [key for key in obj if isinstance(key, basestring) and key[0] in self.chars_to_escape]
            if keys_to_escape:
                new_dct = obj.copy()
                for key in keys_to_escape:
                    new_dct['%s%s' % (self.escape_char, key)] = new_dct.pop(key)
                return json.JSONEncoder.iterencode(self, new_dct, _one_shot)
        return json.JSONEncoder.iterencode(self, obj, _one_shot)


# ---- inbuilt types 

# numeric ( python decimal.Decimal )
def decimal_serialiser(num):
    dct = SerialisationDict()
    dct['#num'] = str(num)
    return dct


def decimal_deserialiser(dct):
    value = decimal.Decimal(dct.pop('#num'))
    if dct:
        raise ValueError('Invalid #num')  # should be an empty dct
    return value


# timestamp ( python datetime.datetime )
def timestamp_serialiser(tstamp):
    dct = SerialisationDict()
    dct['#tstamp'] = tstamp.isoformat()
    return dct


def timestamp_deserialiser(dct):
    value = dateutil.parser.parse(dct.pop('#tstamp'))
    if dct:
        raise ValueError('Invalid #tstamp')  # should be an empty dct
    return value


# date
def date_serialiser(dte):
    dct = SerialisationDict()
    dct['#date'] = dte.isoformat()
    return dct


def date_deserialiser(dct):
    value = datetime.datetime.strptime(dct.pop('#date'), '%Y-%m-%d').date()
    if dct:
        raise ValueError('Invalid #date')  # should be an empty dct
    return value


# time
def time_serialiser(the_time):
    dct = SerialisationDict()
    dct['#time'] = the_time.isoformat()
    return dct


def time_deserialiser(dct):
    value = dateutil.parser.parse(dct.pop('#time')).time()
    if dct:
        raise ValueError('Invalid #time')  # should be an empty dct
    return value


# binary  ( python bytearray - 2.6 and higher )
def binary_serialiser(bin_data):
    dct = SerialisationDict()
    dct['#bin'] = base64.b64encode(bin_data)
    return dct


def binary_deserialiser(dct):
    value = bytearray(base64.b64decode(dct.pop('#bin')))
    if dct:
        raise ValueError('Invalid #bin')  # should be an empty dct
    return value
