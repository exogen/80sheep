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
