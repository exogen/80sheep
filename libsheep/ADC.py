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

# Object wrapper for ADC message
class Message(object):
    def __init__(self,mtype,cmd,headargs={},posargs=[],nameargs={}):
        self.mtype = mtype
        self.cmd = cmd
        self.headargs = headargs
        self.posargs = posargs
        self.nameargs = nameargs

    def shorthand():
        return self.mtype + self.cmd

    
    def encode():
        # Encode message header
        msg = self.mtype + self.cmd

        if mtype == 'B':
            msg += ' ' + base64.b32encode(self.headargs['sid'])
        elif mtype in ['D','E']:
            msg += ' ' + base64.b32encode(self.headargs['sid'])
            msg += ' ' + base64.b32encode(self.headargs['tsid'])
        elif mtype == 'F':
            msg += ' ' + base64.b32encode(self.headargs['sid'])
            msg += ' ' + string.join(self.headargs['features'],'')
        elif mtype == 'U':
            msg += ' ' + base64.b32encode(self.headargs['cid'])

        # Encode message arguments
        for arg in self.posargs:
            msg += " " + self.escape_text(arg)
        for arg in self.nameargs.keys():
            msg += " " + arg + self.escape_text(nameargs[arg])
        msg += "\n"

        #FIXME: Is this really the right place to be doing this?
        encoded = unicodedata.normalize( 'NFC', unicode(msg, 'utf-8') )
        return encoded

    # three escapes are defined
    def escape_text(text):
        escaped = text.replace("\\","\\\\") # escape \ first
        escaped = escaped.replace(" ","\\ ")
        escaped = escaped.replace("\n","\\n")
        return escaped

    def unescape_text(text):
        unescaped = text.replace("\\\\","\\")
        unescaped = unescaped.replace("\\ "," ")
        unescaped = unescaped.replace("\\n","\n")
        return unescaped


# converts string to Message object
def decode(msg):
    if not msg.endswith('\n'):
        raise ProtocolException("Incomplete message: missing newline.")
    
    # Split on spaces, exclude trailing newline.
    tokens = re.split(' ', msg.rstrip('\n'))
    
    # First token.
    token = tokens.pop(0)
    
    # Extract message type and command.
    if token.length < 4:
        raise ProtocolException("Command too short: %r" % (token,))
    
    mtype = token[0]
    cmd = token[1:3]
    
    headargs = decodeHeaderTokens(mtype, tokens)
    cmdargs = decodeCommandTokens(mtype, cmd, tokens)
    
    return Message(mtype, cmd, headargs, cmdargs['pos'], cmdargs['name'])

def decodeHeaderTokens(mtype, tokens):
    headargs = {}
    if mtype == 'B':
        if len(tokens) < 1:
            raise ProtocolException("B msg missing args")
        headargs['sid'] = base64.b32decode(tokens.pop(0))
    elif mtype in 'DE':
        if len(tokens) < 2:
            raise ProtocolException("D|E msg missing args")
        headargs['sid'] = base64.b32decode(tokens.pop(0))
        headargs['tsid'] = base64.b32decode(tokens.pop(0))
    elif mtype == 'F':
        if len(tokens) < 2:
            raise ProtocolException("F msg missing args")
        
        headargs['sid'] = base64.b32decode(tokens.pop(0))
        features_str = tokens.pop(0)
        features = re.findall(r'[+-][A-Z][A-Z0-9]{3}', features_str)
        # Check that the string didn't contain any bozo data.
        if ''.join(features) != features_str:
            raise ProtocolException("Invalid features message: %r", features_str)
        
        headargs['features'] = features
    elif mtype == 'U':
        if len(tokens) < 1:
            raise ProtocolException("U msg missing args")
        headargs['cid'] = base64.b32decode(tokens.pop(0))
    return headargs

def decodeCommandTokens(mtype,cmd,tokens):
    cmd_args['pos'] = []
    cmd_args['name'] = {}
    
    #TODO: This will depend on the individual command =\    
    
#TODO: implement connectHub
# ... something like this...
## api -> connectHub(addr,port=defaultport)
#   connect addr port
#   send( adc_msg( H, SUP, [ADBASE,ADTIGR,...] ) )
#   send( msg_encode('H', 'SUP', {}, ['ADBASE','ADTIGR'])
#   msg = recv( )
#   if(msg.shorthand=='ISUP')
#       hubFeatures(msg.posargs)
#   msg = recv( )
#   if(msg.shorthand=='ISID')
#       SID = msg.headargs['sid']
#   recv ISID <client-sid>
#   * recv IINF HU1 HI1 ...
#   * send BINF <my-sid> ID... PD...
#   recv IGPA ...
#   send HPAS ...
#   recv BINF <all clients>
#   recv BINF <Client-SID>
#   ... provide hub id information for further communication
#   * = optional


