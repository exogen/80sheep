from nose.tools import assert_raises
from libsheep.protocol import Message, MessagePart

def test_message_args_set_message_parts():
    m = Message('H', 'SUP')
    assert isinstance(m.context, MessagePart)
    assert isinstance(m.command, MessagePart)
