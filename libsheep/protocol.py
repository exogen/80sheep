from libsheep.parameters import ParameterCollection

class ProtocolError(RuntimeError):
    pass

class MessagePart(object):
    __metaclass__ = ParameterCollection
    
    def __new__(cls, code, *args, **kwargs):
        handler_class = cls.REGISTRY.get(code, cls)
        instance = object.__new__(handler_class, code, *args, **kwargs)
        return instance
    
    def __init__(self, code):
        self.code = code
    
    def __get__(self, instance, owner):
        if instance is not None:
            _msg_parts = instance.__dict__.get('_msg_parts', {})
            return _msg_parts.get(self, self)
        else:
            return self
    
    def __set__(self, instance, value):
        if not isinstance(value, MessagePart):
            value = self.__class__(value)
        _msg_parts = instance.__dict__.setdefault('_msg_parts', {})
        _msg_parts[self] = value
    
    @classmethod
    def register(cls, *codes):
        if not codes:
            codes = [cls.__name__]
        for code in codes:
            cls.REGISTRY[code] = cls

class Context(MessagePart):
    REGISTRY = {}
    
    def __repr__(self):
        return "Context(%r)" % self.code

class Command(MessagePart):
    REGISTRY = {}
    
    def __repr__(self):
        return "Command(%r)" % self.code

class Message(object):
    context = Context(None)
    command = Command(None)
        
    def __init__(self, context, command):
        self.context = context
        self.command = command
    
    def __repr__(self):
        return "Message(%r, %r)" % (self.context.code, self.command.code)
    
    @classmethod
    def decode(cls, tokens):
        if isinstance(tokens, basestring):
            tokens = tokens.split()
        else:
            tokens = list(tokens)
        try:
            token = tokens.pop(0)
        except IndexError:
            raise ProtocolError("No message header found.")
        else:
            if len(token) == 4:
                context = token[0]
                command = token[1:]
                message = cls(context, command)
                return message
            else:
                raise ProtocolError("No leading four-letter word in header.")
        
# Message context handlers.

class B(Context):
    source_sid = Parameter(0, Base32)

class CIH(Context):
    pass

class DE(Context):
    source_sid = Parameter(0, Base32)
    target_sid = Parameter(1, Base32)

class U(Context):
    source_cid = Parameter(0, Base32)

class F(Context):
    source_sid = Parameter(0, Base32)
    required_features = Parameter(1, Set(re.compile(r'[+][A-Z][A-Z0-9]{3}')))
    excluded_features = Parameter(1, Set(re.compile(r'[-][A-Z][A-Z0-9]{3}')))

# Register context handlers.

B.register()
CIH.register('C', 'I', 'H')
DE.register('D', 'E')
U.register()
F.register()