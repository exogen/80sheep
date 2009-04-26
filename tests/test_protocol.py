from nose.tools import assert_raises
from libsheep.protocol import Message, MessagePart, Context, Command

def test_message_args_set_message_parts():
    m = Message('H', 'SUP')
    assert isinstance(m.context, MessagePart)
    assert isinstance(m.command, MessagePart)

def test_message_parts_have_arg_codes():
    m = Message('H', 'SUP')
    assert m.context.code == 'H'
    assert m.command.code == 'SUP'

def test_h_context_creates_h_instance():
    from libsheep.protocol import CIH
    context = Context('H')
    assert isinstance(context, CIH)

def test_unknown_context_creates_generic_instance():
    context = Context('Z')
    assert type(context) is Context

def test_message_decode_parses_message():
    m = Message.decode('HSUP ADBASE ADTIGR')
    assert isinstance(m, Message)
