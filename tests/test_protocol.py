from nose.tools import assert_raises
from libsheep.protocol import Message, MessagePart

def test_message_args_set_message_parts():
    m = Message('H', 'SUP')
    assert isinstance(m.context, MessagePart)
    assert isinstance(m.command, MessagePart)

def test_message_parts_have_arg_codes():
    m = Message('H', 'SUP')
    assert m.context.code == 'H'
    assert m.command.code == 'SUP'
