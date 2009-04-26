#!/usr/bin/env python
import unittest
from libsheep.path import Path


class TestEscapeName(unittest.TestCase):
    def test_slashes_escaped(self):
        self.assertEquals(Path.escape(r'//'), r'\/\/')
    
    def test_backslashes_escaped(self):
        self.assertEquals(Path.escape('\\\\'), r'\\\\')
    
    def test_other_punctuation_unescaped(self):
        s = '`~!@#$%^&*()-_=+[{]}|;:\'",<.>?'
        self.assertEquals(Path.escape(s), s)


class TestUnescapeName(unittest.TestCase):
    def test_slashes_unescaped(self):
        self.assertEquals(Path.unescape(r'\/\/'), r'//')
    
    def test_backslashes_unescaped(self):
        self.assertEquals(Path.unescape(r'\\\\'), '\\\\')
    
    def test_unknown_escape_sequence_is_literal_char(self):
        self.assertEquals(Path.unescape(r'\x'), 'x')


class TestSplitPath(unittest.TestCase):
    def test_no_slash_gives_same_string(self):
        self.assertEquals(Path('one').names, ('one',))
    
    def test_slash_splits_path(self):
        self.assertEquals(Path('one/two/three'), ('one', 'two', 'three',))
    
    def test_trailing_slash_trailing_empty_string(self):
        self.assertEquals(Path('one/')[-1], '')
        self.assertEquals(Path('one/two/')[-1], '')
    
    def test_leading_slash_leading_empty_string(self):
        self.assertEquals(Path('/')[0], '')
        self.assertEquals(Path('/one')[0], '')
    
    def test_duplicate_slashes_ignored(self):
        self.assertEquals(Path('//'), Path('/'))
        self.assertEquals(Path('///'), Path('/'))
        self.assertEquals(Path('one//two'), Path('one/two'))
        self.assertEquals(Path('one///two'), Path('one/two'))
        self.assertEquals(Path('//one//'), Path('/one/'))
        self.assertEquals(Path('///one///'), Path('/one/'))
    
    def test_escaped_slashes_do_not_split(self):
        self.assertEquals(len(Path(r'a\/b')), 1)
        self.assertEquals(len(Path(r'a\/\/b')), 1)
    
    def test_split_names_are_escaped(self):
        self.assertEquals(Path(r'a\\b').names, (r'a\b',))
        self.assertEquals(Path(r'a\/b').names, (r'a/b',))
        self.assertEquals(Path(r'a\xb').names, (r'axb',))


class TestJoinNames(unittest.TestCase):
    def test_names_are_joined_by_slashes(self):
        self.assertEquals(Path(['', '']).string, '/')
        self.assertEquals(Path(['one', 'two']).string, 'one/two')
    
    def test_joined_names_are_escaped(self):
        self.assertEquals(Path(['a/b', 'c\\d']).string, 'a\\/b/c\\\\d')

def test_parent_of_directory_is_directory_parent():
    assert Path('a/b/').parent == Path('a/')

def test_parent_of_file_is_its_directory():
    assert Path('a/b').parent == Path('a/')

def test_parent_of_root_is_none():
    assert Path('/').parent == None
    assert Path('a').parent == None

def test_root_of_path_is_path_root():
    assert Path('a/b/c').root == 'a'
    assert Path('a').root == None

def test_join_filenames_gives_second_filename():
    assert Path('a').join('b') == Path('b')

def test_join_paths_joins_paths():
    assert Path('a/').join('b') == Path('a/b')

def test_join_with_absolute_path_stomps_path():
    assert Path('a/b/c').join('/foo') == Path('/foo')

def test_repr_shows_path_representation():
    assert repr(Path(['a','b','c'])) == "Path(u'a/b/c')"

def test_file_is_file():
    assert Path('a').is_file
    assert not Path('a').is_directory

def test_directory_is_directory():
    assert Path('a/').is_directory
    assert not Path('a/').is_file

if __name__ == '__main__':
    unittest.main()
