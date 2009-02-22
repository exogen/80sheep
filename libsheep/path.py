#!/usr/bin/env python
"""
Module for handling filename construction, manipulation, and validation.
These features are encapsulated in the `Path` class.  `Path` instances offer
access to the filename both as a string and as a sequence containing the root
name, directory names, and file name; names in this sequence have been
unescaped.

Filenames created with `Path` are not required to be absolute, which means
they are not necessarily relative to the unnamed root '/'.  Absolute `Path`
instances are identifiable in several (ultimately equivalent) ways:
    
    * The `string` property begins with '/'.
    * The `is_absolute` property is True.
    * The `is_relative` property is False.
    * The `root` property is the empty string '', signifying the unnamed root.
    * The first string in the `names` property is empty.

Constructing an invalid filename will raise an `InvalidPath` exception.
Invalid filenames include:

    * The empty string.
    * Those explicitly constructed with an empty intermediate directory name.
    * Those containing the names '.' or '..', which have special meaning.
    * Those containing names with unprintable characters.

"""
import logging
import re
from libsheep.utils import is_printable

log = logging.getLogger(__name__)

class InvalidPath(Exception):
    pass

class Path(object):
    ESCAPED_CHAR = re.compile(r'\\(.?)')
    SPECIAL_CHARS = re.compile(r'(/|\\.?)')
    SPECIAL_NAMES = set(['.', '..'])
    
    @classmethod
    def escape(cls, name):
        """Escape slashes and backslashes in the string `name`."""
        # `str.replace` is faster than `re.sub` in this case.
        return name.replace('\\', '\\\\').replace('/', '\\/')
    
    @classmethod
    def unescape(cls, string):
        """
        Replace escape sequences in `string` to get the literal name instead
        of its escaped representation.
        
        Unknown escape sequences (characters other than '/' or the escape
        character) are replaced with the literal character.  For instance,
        '\z' will be replaced with 'z'.  A trailing escape character resulting
        in an incomplete escape sequence will be stripped.
        
        """
        return cls.ESCAPED_CHAR.sub(r'\1', string)
    
    @classmethod
    def _split(cls, filename):
        """
        Split the string `filename` into its component names, each separated
        by a '/', and return them in a list.  Component names may contain
        escaped '/' and escape characters; the returned names remain escaped.
        
        If the filename is absolute (it begins with '/'), the first item is
        an empty string:
        
        >>> Path._split('/')[0]
        ''
        >>> Path._split('/dir/subdir/filename.ext')[0]
        ''
        
        If the filename references a directory (it has a trailing unescaped
        '/'), the last item will be an empty string:
        
        >>> Path._split('/dir/subdir/')[-1]
        ''
        
        Otherwise, the last item will be the name of the file:
        
        >>> Path._split('/dir/subdir/filename.ext')[-1]
        'filename.ext'
        
        Thus, the filename referencing the fictive root, '/', splits into a
        list of two empty strings:
        
        >>> Path._split('/')
        ['', '']
        
        Duplicate slashes are forgiven; directory names may not be empty:
        
        >>> Path._split('one//two')
        ['one', 'two']
        
        Literal slashes that appear in component names must be escaped to
        avoid splitting:
        
        >>> Path._split('one\\\\/two')
        ['one\\\\/two']
        
        """
        # This is not as simple as splitting on '/' due to escape sequences.
        # Testing revealed that splitting on this simple regex and processing
        # the results is faster than using a more sophisticated regex.
        pieces = cls.SPECIAL_CHARS.split(filename)
        names = []
        name = ''
        for piece in pieces:
            if piece != '/':
                # This string is part of a directory or filename.
                name += piece
            elif name or not names:
                # Found a separator; add the previous name only if it would
                # be valid to do so.
                names.append(name)
                name = ''
        names.append(name)
        return names
    
    @classmethod
    def _join(cls, names):
        return u'/'.join(map(cls.escape, names))
    
    def __init__(self, path):
        if isinstance(path, basestring):
            self.string = path
        elif isinstance(path, Path):
            self._names = path._names
            self._string = path._string
            self._key = path._key
        else:
            self.names = path
    
    def __iter__(self):
        return iter(self.names)
    
    def __len__(self):
        return len(self.names)
    
    def __getitem__(self, item):
        return self.names[item]
    
    def __eq__(self, other):
        if isinstance(other, Path):
            return self._key == other._key
        else:
            return self == Path(other)
    
    def __ne__(self, other):
        return not self == other
    
    def __repr__(self):
        return 'Path(%r)' % (self.string,)
    
    def __str__(self):
        return self.string
    
    @property
    def parent(self):
        names = list(self)
        if self.is_directory:
            names[-2:] = ['']
        else:
            names[-1] = ''
        if len(names) > 1:
            return Path(names)
    
    @property
    def is_directory(self):
        return not self.names[-1]
    
    @property
    def is_file(self):
        return not self.is_directory
    
    @property
    def is_absolute(self):
        return not self.names[0]
    
    @property
    def is_relative(self):
        return not self.is_absolute
    
    @property
    def root(self):
        if len(self.names) > 1:
            return self[0]
    
    def join(self, other):
        other = Path(other)
        if other.is_relative:
            return Path(self[:-1] + other.names)
        else:
            return other
    
    def is_ancestor(self, other, inclusive=True):
        other = Path(other)
        if self.is_directory:
            if other._key.startswith(self._key):
                return inclusive or self != other
        return False
    
    def descends_from(self, other, inclusive=True):
        return Path(other).is_ancestor(self, inclusive)
    
    def relative_to(self, base):
        base = Path(base)
        if not base.is_directory:
            base = base.parent
        if base.is_absolute:
            if self.descends_from(base):
                return Path(self.names[len(base) - 1:])
            else:
                raise RuntimeError("Path does not descend from base.")
        else:
            raise RuntimeError("Base is not absolute.")
    
    def _get_names(self):
        return self._names
    
    def _set_names(self, value):
        names = tuple(value)
        count = len(names)
        
        # Validate the path's names. 
        if count > 1 and '' in names[1:-1]:
            # Names between the first and last must not be empty.
            raise InvalidPath("Empty directory name.")
        elif count == 1 and '' in names:
            # Relative path; the single name must not be empty.
            raise InvalidPath("Empty top-level (relative) filename.")
        elif not count:
            raise InvalidPath("Empty path.")
        # Check for invalid names.
        for name in names:
            if name in self.SPECIAL_NAMES:
                raise InvalidPath("Filename conflicts with special name: %r" % (name,))
            elif not is_printable(name):
                raise InvalidPath("Filename has unprintable characters: %r" % (name,))
        
        self._names = names
        self._string = self._join(names)
        self._key = self._string.lower()
    
    names = property(_get_names, _set_names)
    
    def _get_string(self):
        return self._string
    
    def _set_string(self, value):
        self.names = map(self.unescape, self._split(value))
    
    string = property(_get_string, _set_string)
