from nose.tools import assert_raises
from libsheep.protocol import Message, MessagePart, Context, Command
from libsheep.features.base import BASE, SUP

def test_disabled_base_feature_decodes_generic_instance():
    m = Message.decode('HSUP ADBASE ADTIGR')
    assert type(m.command) is Command

def test_enabled_base_features_decodes_command_instance():
    BASE().enable()
    m = Message.decode('HSUP ADBASE ADTIGR')
    assert isinstance(m.command, SUP)

# def test_sup_command():
#     m = Message.decode('HSUP ADBASE ADTIGR')
#     assert m.command.add_features == set(['BASE', 'TIGR'])
#     assert m.command.remove_features == set([])