#### MESSAGE SYNTAX (from ADC spec) ####
#message               ::= message_body? eol
#message_body          ::= (b_message_header | cih_message_header | de_message_header | f_message_header | u_message_header | message_header) (separator positional_parameter)* (separator named_parameter)*
#b_message_header      ::= 'B' command_name separator my_sid
#cih_message_header    ::= ('C' | 'I' | 'H') command_name
#de_message_header     ::= ('D' | 'E') command_name separator my_sid separator target_sid
#f_message_header      ::= 'F' command_name separator my_sid separator (('+'|'-') feature_name)+
#u_message_header      ::= 'U' command_name separator my_cid
#command_name          ::= simple_alpha simple_alphanum simple_alphanum
#positional_parameter  ::= parameter_value
#named_parameter       ::= parameter_name parameter_value?
#parameter_name        ::= simple_alpha simple_alphanum
#parameter_value       ::= escaped_letter+
#target_sid            ::= encoded_sid
#my_sid                ::= encoded_sid
#encoded_sid           ::= base32_character{4}
#my_cid                ::= encoded_cid
#encoded_cid           ::= base32_character+
#base32_character      ::= simple_alpha | [2-7]
#feature_name          ::= simple_alpha simple_alphanum{3}
#escaped_letter        ::= [^ \#x0a] | escape 's' | escape 'n' | escape escape
#escape                ::= '\'
#simple_alpha          ::= [A-Z]
#simple_alphanum       ::= [A-Z0-9]
#eol                   ::= #x0a
#separator             ::= ' '

#############################################

# load modules
import unicodedata
import base64
import string
import re



class Message(object):
    """Wrapper object for ADC messages."""
    
    FEATURE_RE = re.compile(r'[+-][A-Z][A-Z0-9]{3}')
    REGISTRY = {}
    
    @classmethod
    def register(cls, type, encoder=None, decoder=None):
        cls.REGISTRY[type] = (encoder, decoder)
    
    @classmethod
    def decode(cls, msg):
        """Convert string `msg` to `Message` instance."""
        tokens = msg.split(' ') # Split on space.
        first = cls.consume(tokens) # First determines how to consume the rest.
        if len(first) == 4:
            message_type = first[0]
            command = first[1:]
            message = cls(message_type, command)
            if message_type in cls.REGISTRY:
                encoder, decoder = cls.REGISTRY[message_type]
                if callable(decoder):
                    decoder(message, tokens)
            else:
                raise ProtocolException("Unrecognized message type: %r" % message_type)
            return message
        else:
            raise ProtocolException("Invalid header token: %r" % first)
    
    @classmethod
    def get_params(cls, tokens):
        for token in tokens:
            token = cls.unescape(token)
            name = token[:2]
            value = token[2:]
            yield (name, value)
    
    @classmethod
    def consume(cls, tokens, decode_func=None):
        try:
            token = tokens.pop(0)
        except IndexError:
            raise ProtocolException("Expected token not found.")
        else:
            if callable(decode_func):
                token = decode_func(token)
            return token
    
    @classmethod
    def escape(cls, text):
        # Three escapes are defined.
        escaped = text.replace('\\', '\\\\')
        escaped = escaped.replace(' ', '\\s')
        escaped = escaped.replace('\n', '\\n')
        return escaped
    
    @classmethod
    def unescape(cls, text):
        unescaped = text.replace('\\\\', '\\')
        unescaped = unescaped.replace('\\s', ' ')
        unescaped = unescaped.replace('\\n', '\n')
        return unicode(unescaped)
    
    def __init__(self, type, command):
        self.type = type
        self.command = command
        self.params = []
    
    def __repr__(self):
        return "Message(%r, %r)" % (self.type, self.command)
    
    def decode_B_header(self, tokens):
        self.my_sid = self.consume(tokens, base64.b32decode)
    
    def encode_B_header(self):
        yield base64.b32encode(self.my_sid)
    
    def decode_DE_header(self, tokens):
        self.my_sid = self.consume(tokens, base64.b32decode)
        self.target_sid = self.consume(tokens, base64.b32decode)
    
    def encode_DE_header(self):
        yield base64.b32encode(self.my_sid)
        yield base64.b32encode(self.target_sid)
    
    def decode_F_header(self, tokens):
        self.my_sid = self.consume(tokens, base64.b32decode)
        feature_sets = {}
        self.required_features = feature_sets['+'] = set([])
        self.excluded_features = feature_sets['-'] = set([])
        for feature in self.consume(tokens, self.FEATURE_RE.findall):
            rule = feature[0]
            name = feature[1:]
            feature_sets[rule].add(name)
    
    def encode_F_header(self):
        yield base64.b32encode(self.my_sid)
        yield ''.join(['+%s' % feature for feature in self.required_features] +
                      ['-%s' % feature for feature in self.excluded_features])
    
    def decode_U_header(self, tokens):
        self.my_cid = self.consume(tokens, base64.b32decode)
    
    def encode_U_header(self, tokens):
        yield base64.b32encode(self.my_cid)
    
    def decode_STA_params(self, tokens):
        code = self.consume(tokens)
        self.description = self.consume(tokens, self.unescape)
        self.severity = code[0]
        self.error_code = code[1:3]
    
    def SUP(self, tokens):
        pass
    
    def SID(self, tokens):
        self.sid = self.consume(tokens, base64.b32decode)
    
    def INF(self, tokens):
        pass
    
    def MSG(self, tokens):
        self.text = self.consume(tokens, self.unescape)
    
    def SCH(self, tokens):
        self.params[:] = self.get_params(tokens)
    
    def RES(self, tokens):
        self.params[:] = self.get_params(tokens)
    
    def decode_CTM_params(self, tokens):
        self.protocol = self.consume(tokens)
        self.port = self.consume(tokens, int)
        self.token = self.consume(tokens)
    
    def decode_RCM_params(self, tokens):
        self.protocol = self.consume(tokens)
        self.token = self.consume(tokens)
    
    def decode_GPA_params(self, tokens):
        self.data = self.consume(tokens, base64.b32decode)
    
    def decode_PAS_params(self, tokens):
        self.password = self.consume(tokens, base64.b32decode)
    
    def decode_QUI_params(self, tokens):
        self.session_id = self.consume(tokens, base64.b32decode)
    
    def decode_GET_params(self, tokens):
        
    
    def decode_GFI_params(self, tokens):
        pass
    
    def decode_SND_params(self, tokens):
        pass
    
    def encode(self):
        # Encode message header.
        tokens = ['%s%s' % (self.type, self.command)]
        if self.type in self.REGISTRY:
            encoder, decoder = cls.REGISTRY[message_type]
            if callable(encoder):
                tokens.extend(encoder(message))
        
        # Encode message parameters.
        for arg in self.posargs:
            msg += " " + self.escape_text(arg)
        for arg in self.nameargs.keys():
            msg += " " + arg + self.escape_text(nameargs[arg])
        
        # FIXME: Is this really the right place to be doing this?
        return unicodedata.normalize('NFC', u' '.join(tokens)).encode('utf-8')

Message.register('B', Message.encode_B_header, Message.decode_B_header)
Message.register('C')
Message.register('I')
Message.register('H')
Message.register('D', Message.encode_DE_header, Message.decode_DE_header)
Message.register('E', Message.encode_DE_header, Message.decode_DE_header)
Message.register('F', Message.encode_F_header, Message.decode_F_header)
Message.register('U', Message.encode_U_header, Message.decode_U_header)

class Header(object):
    pass

class Command(object):
    pass

class SUP(Command):
    pass

class STA(Command):
    pass

# Handshake goes something like this.
# Enter stage PROTOCOL.
# -> HSUP ADBASE ADTIGR ...
# <- ISUP ADBASE ADTIGR ...
# <- ISID <sid>
# [<- IINF HU1 HI1 ...]
# Enter stage IDENTIFY.
# -> BINF <sid> ID... PD... 
# [Enter stage VERIFY.]
# <- IGPA ...
# -> HPAS ...
# Enter stage NORMAL.
# If not sent previously:
# <- IINF HU1 HI1 ...
# For each client in NORMAL state:
# <- BINF ...
# For connecting client:
# <- BINF ...
