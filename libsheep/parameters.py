class ParameterType(object):
    def encode(self, value):
        return value
    
    def decode(self, data):
        return data
    
    def extract_data(self, data):
        return data[0][self.slice]

class String(ParameterType):
    pass

class Base32(ParameterType):
    def encode(self, value):
        yield base64.b32encode(value)
    
    def decode(self, data):
        return base64.b32decode(data)

class Set(ParameterType):
    def __init__(self, finder=None, type=None):
        self.finder = finder
        self.type = type
    
    def decode(self, data):
        values = set([])
        for value in data:
            if self.type is not None:
                value = self.type(value)
            values.add(value)
        return values
    
    def encode(self, values):
        for value in values:
            yield unicode(value)
    
    def extract_data(self, data):
        return data[self.slice]

class Flag(ParameterType):
    def encode(self, value):
        if value:
            yield ''
        else:
            yield None
    
    def decode(self, data):
        return True

class Delimited(ParameterType):
    def __init__(self, delimiter=','):
        self.delimiter = delimiter
    
    def encode(self, value):
        return self.delimiter.join(map(unicode, value))
    
    def decode(self, data):
        return data.split(self.delimiter)

class Integer(ParameterType):
    def encode(self, value):
        yield unicode(value)
    
    def decode(self, data):
        return int(data)

class Boolean(ParameterType):
    def encode(self, value):
        if value:
            yield '1'
        else:
            yield '0'
    
    def decode(self, data):
        if data in '0':
            return False
        else:
            return True

class BitField(ParameterType):
    def __init__(self, bits):
        self.bits = bits
    
    def encode(self, value):
        bits = 0
        for item in value:
            try:
                index = self.bits.index(item)
            except ValueError:
                pass
            else:
                bits |= index + 1
        return str(bits)
    
    def decode(self, data):
        bits = int(data)
        value = set([])
        for i, item in enumerate(self.bits):
            if bits & (2 ** i):
                value.add(item)
        return value

class Parameter(object):
    STATE_ATTR = '_param_state'
    
    def __init__(self, key, type=String(), default=None):
        if not isinstance(type, ParameterType) and callable(type):
            type = type()
        self.key = key
        self.type = type
        self.default = default
        self.slice = slice(None)
    
    def __get__(self, instance, owner):
        if instance is not None:
            _param_state = instance.__dict__.get(self.STATE_ATTR, {})
            return _param_state.get(self, self.default)
        else:
            return self
    
    def __set__(self, instance, value):
        _param_state = instance.__dict__.setdefault(self.STATE_ATTR, {})
        _param_state[self] = value
    
    def __getitem__(self, item):
        self.slice = item
    
    def encode(self, value):
        return self.type.encode(value)
    
    def decode(self, data):
        return self.type.decode(data)
    
    def extract_data(self, data):
        return self.type.extract_data(data)

class ParameterCollection(type):
    def __new__(cls, name, bases, attrs):
        param_attrs = attrs['_param_attrs'] = {}
        param_keys = attrs['_param_keys'] = {}
        for attr, value in attrs.iteritems():
            if isinstance(value, Parameter):
                param_attrs[attr] = value
                param_keys.setdefault(value.key, []).append(value)
        return type.__new__(cls, name, bases, attrs)
