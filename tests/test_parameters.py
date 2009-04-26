from nose.tools import assert_raises
from libsheep.parameters import ParameterCollection, Parameter, String

def test_parameter_integer_argument_sets_key():
    p = Parameter(0)
    assert p.key == 0

def test_parameter_string_argument_sets_key():
    p = Parameter('AD')
    assert p.key == 'AD'

def test_parameter_type_argument_sets_type():
    parameter_type = String()
    p = Parameter(0, parameter_type)
    assert p.type is parameter_type

def test_parameter_type_class_argument_creates_type_instance():
    p = Parameter(0, String)
    assert isinstance(p.type, String)

def test_parameter_type_defaults_to_string():
    p = Parameter(0)
    assert isinstance(p.type, String)

def test_parameter_requires_key_argument():
    assert_raises(TypeError, Parameter)
    
def test_parameter_collection_can_add_parameters():
    params = ParameterCollection()
    p = Parameter(0)
    params.add(p)
    assert p in params
