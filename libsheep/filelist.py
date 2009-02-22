#!/usr/bin/env python
import logging
import re
import copy
try:
    from xml.etree import ElementTree
except ImportError:
    import ElementTree
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from libsheep.path import Path

log = logging.getLogger(__name__)

class NotFound(Exception):
    pass

class File(object):
    def __init__(self, name, size, **kwargs):
        self.name = name
        self.size = size
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    
    def __repr__(self):
        return 'File(%r, %r)' % (self.name, self.size)
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __ne__(self, other):
        return not self == other
    
    @classmethod
    def from_element(cls, element):
        name = element.attrib['Name']
        size = int(element.attrib['Size'])
        # TODO: Optional/arbitrary attributes (from extensions, etc.)
        return cls(name, size)
    
    def to_element(self):
        element = ElementTree.Element('File')
        element.set('Name', self.name)
        element.set('Size', '%d' % (self.size,))
        # TODO: Optional/arbitrary attributes (from extensions, etc.)
        return element

class Container(object):
    """
    Base class for `Directory` and `FileListing`, which can both contain
    `File` instances and other `Container` instances.
    
    """
    
    def __init__(self):
        self.contents = {}
    
    def __iter__(self):
        return self.contents.itervalues()
    
    def __len__(self):
        return len(self.contents)
    
    def __nonzero__(self):
        return bool(self.contents)
    
    def __contains__(self, name):
        return name in self.contents
    
    def __getitem__(self, name):
        try:
            return self.contents[name]
        except KeyError:
            raise NotFound("%r" % (name,))
    
    def __setitem__(self, name, item):
        self.contents[name] = item
    
    def __delitem__(self, name):
        try:
            del self.contents[name]
        except KeyError:
            raise NotFound("%r" % (name,))
    
    def __eq__(self, other):
        if isinstance(other, Container):
            return self.contents == other.contents
        else:
            return False
    
    def __ne__(self, other):
        return not self == other
    
    def add(self, path, overwrite=False, **kwargs):
        """
        Add an item to this container at the relative path `path` and return
        the added item.  If the path references a directory, the item will be
        a `Directory` instance, otherwise it will be a `File` instance.
        Intermediate directories will be created as needed.
        
        Existing items referenced by `path`, including intermediate
        directories, will raise a `RuntimeError` if they are not of the
        correct type (`Container` or `File`).
        
        If `overwrite` is True, then intermediate directories in `path` that
        currently reference files will be replaced with new `Directory`
        instances, and any item sharing the same path will be replaced with a
        new `File` or `Directory` instance.
        
        """
        path = Path(path)
        if not path.is_relative:
            raise RuntimeError("Path must be relative to container.")
        
        parent = self
        # Descend the tree named by `path`, creating intermediate directories
        # as needed.
        for dir_name in path.names[:-1]:
            item = parent.contents.get(dir_name)
            if isinstance(item, Container):
                # Directory exists.
                parent = item
            elif item is None or overwrite:
                # Directory does not exist or can be replaced.
                parent[dir_name] = parent = Directory(dir_name)
            else:
                # A non-directory of the same name exists, but should not be
                # overwritten.
                raise RuntimeError("%r exists and is not a directory "
                                   "(try overwrite=True)." % (dir_name,))
        
        file_name = path.names[-1]
        if file_name:
            item = parent.contents.get(file_name)
            if item is None or overwrite:
                parent[file_name] = item = File(file_name, None)
            elif not isinstance(item, File):
                raise RuntimeError("%r exists and is not a file "
                                   "(try overwrite=True)." % (file_name,))
        else:
            item = parent
        for key, value in kwargs.iteritems():
            setattr(item, key, value)
        return item
    
    def remove(self, path):
        """
        Remove the item at the relative path `path` from this container and
        return the item.  If no such item is found, return None.
        
        If `path` references a directory, then the item must be a `Container`
        instance to match.  Otherwise, items of any type will match.  For
        example, removing 'one/two' will remove any item named 'two', and
        removing 'one/two/' will only remove a directory named 'two'.
        
        """
        path = Path(path)
        if not path.is_relative:
            raise RuntimeError("Path must be relative to container.")
        
        grandparent = None
        parent = self
        for dir_name in path.names[:-1]:
            grandparent = parent
            parent = parent.contents.get(dir_name)
            if not isinstance(parent, Container):
                break
        else:
            file_name = path.names[-1]
            if file_name:
                if file_name in parent:
                    item = parent[file_name]
                    del parent[file_name]
                    return item
            elif grandparent is not None:
                item = grandparent[dir_name]
                del grandparent[dir_name]
                return item
    
    def iter_paths(self, base=None, depth=-1):
        names = base and Path(base).names[:-1] or ()
        for item in self:
            if isinstance(item, Container):
                path = Path(names + (item.name, ''))
                yield (path, item)
                if depth:
                    for child_path, child in item.iter_paths(path, depth - 1):
                        yield (child_path, child)
            else:
                path = Path(names + (item.name,))
                yield (path, item)
    
    def get_partial(self, depth=0):
        partial = copy.copy(self)
        partial.contents = {}
        if depth:
            for name, item in self.contents.iteritems():
                if isinstance(item, Container):
                    partial.contents[name] = item.get_partial(depth - 1)
                else:
                    partial.contents[name] = copy.copy(item)
        return partial

class Directory(Container):
    """
    High-level representation of a shared directory.
    
    """
    def __init__(self, name, incomplete=False, **kwargs):
        """
        Create a Directory instance with the given `name`, which is the
        unescaped name without a trailing '/'.
        
        """
        super(Directory, self).__init__()
        self.name = name
        self.incomplete = incomplete
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    
    def __repr__(self):
        return 'Directory(%r, %r)' % (self.name, self.incomplete)
    
    def __eq__(self, other):
        if isinstance(other, Directory):
            if self.name != other.name or self.incomplete != other.incomplete:
                return False
        return super(Directory, self).__eq__(other)
    
    @classmethod
    def from_element(cls, element):
        name = element.attrib['Name']
        incomplete = bool(element.get('Incomplete', False))
        # TODO: Optional/arbitrary attributes (from extensions, etc.)
        # Create a `Directory` instance.
        directory = cls(name, incomplete)
        
        # Add files and directories to the instance.
        for subelement in element:
            if subelement.tag == 'File':
                child_file = File.from_element(subelement)
                directory.contents[child_file.name] = child_file
            elif subelement.tag == 'Directory':
                child_dir = cls.from_element(subelement)
                directory.contents[child_dir.name] = child_dir
        
        return directory
    
    def to_element(self):
        element = ElementTree.Element('Directory')
        element.set('Name', self.name)
        if self.incomplete:
            element.set('Incomplete', str(int(self.incomplete)))
        for child in self.contents.itervalues():
            element.append(child.to_element())
        # TODO: Optional/arbitrary attributes (from extensions, etc.)
        return element

    def get_partial(self, depth=0):
        partial = super(Directory, self).get_partial(depth)
        if self and not partial:
            partial.incomplete = True
        return partial

class FileListing(Container):
    """High-level representation of a file listing."""
    
    VERSION = 1
    GENERATOR = 'libsheep'
    
    def __init__(self, client_id, base='/', version=VERSION, generator=None):
        super(FileListing, self).__init__()
        self.client_id = client_id
        self.base = Path(base)
        if version != self.VERSION:
            raise RuntimeError("Unsupported file listing version.")
        self.version = version
        self.generator = generator
    
    def __repr__(self):
        return 'FileListing(%r, %r)' % (self.client_id, self.base)
    
    def __eq__(self, other):
        if isinstance(other, FileListing):
            if self.client_id != other.client_id or self.base != other.base:
                return False
        return super(FileListing, self).__eq__(other)
    
    def iter_paths(self, depth=-1):
        return super(FileListing, self).iter_paths(self.base, depth)
    
    def _get_base(self):
        return self._base
    
    def _set_base(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        self._base = path
    
    base = property(_get_base, _set_base)
    
    @classmethod
    def from_file(cls, file_or_name):
        """
        Return a `FileListing` instance initialized with contents from
        `file_or_name`, which is a filename or file-like object.
        
        """
        tree = ElementTree.parse(file_or_name)
        return cls.from_element(tree.getroot())
    
    @classmethod
    def from_string(cls, xml_string):
        """
        Return a `FileListing` instance initialized with contents from
        `xml_string`.
        
        """
        element = ElementTree.fromstring(xml_string)
        return cls.from_element(element)
    
    @classmethod
    def from_element(cls, element):
        if element.tag == 'FileListing':
            client_id = element.attrib['CID']
            base = element.attrib['Base']
            version = int(element.attrib['Version'])
            generator = element.get('Generator')
            # TODO: Optional/arbitrary attributes (from extensions, etc.)
            # Create a `FileListing` instance.
            listing = cls(client_id, base, version, generator)
            
            # Add files and directories to the instance.
            for subelement in element:
                if subelement.tag == 'File':
                    listing_file = File.from_element(subelement)
                    listing.contents[listing_file.name] = listing_file
                elif subelement.tag == 'Directory':
                    listing_dir = Directory.from_element(subelement)
                    listing.contents[listing_dir.name] = listing_dir
            
            return listing
        else:
            raise RuntimeError("File listing does not conform to schema.")
    
    def to_element(self):
        element = ElementTree.Element('FileListing')
        element.set('CID', str(self.client_id))
        element.set('Base', unicode(self.base))
        element.set('Version', str(self.version))
        element.set('Generator', self.GENERATOR)
        for child in self.contents.itervalues():
            element.append(child.to_element())
        return element
    
    def serialize(self):
        """Generate and return the XML serialization of the file listing."""
        string_file = StringIO()
        self.write(string_file)
        return string_file.getvalue()
    
    def write(self, file_or_name, mode='w'):
        """
        Serialize the file listing and write it to `file_or_name`, which
        is a filename or file-like object.  If `file_or_name` is a filename,
        it will be opened with the mode given by `mode`.
        
        """
        if isinstance(file_or_name, basestring):
            output_file = open(file_or_name, mode)
        else:
            output_file = file_or_name
        
        root = self.to_element()
        tree = ElementTree.ElementTree(root)
        tree.write(output_file, 'utf-8')
    
    def get(self, path):
        path = Path(path)
        if path.is_absolute:
            # Make this possible later.
            raise RuntimeError("Path does not descend from base.")
        
        names = list(self.base)
        file_name = names.pop()
        parent = self
        for dir_name in names:
            parent = parent[dir_name]
            if not isinstance(parent, Container):
                raise RuntimeError("File not found.")
        if file_name:
            item = parent[file_name]
        else:
            item = parent
        return item
    
    def add(self, path, overwrite=False, **kwargs):
        """
        Add an item to this file listing at the relative or absolute path
        `path` and return the added item.  If the path is absolute, it must
        descend from `self.base`.
        
        See the documentation for `Container.add` for more details.
        
        """
        path = Path(path)
        if path.is_absolute:
            # This is an absolute path.  Ensure that `path` descends from
            # `self.base`, otherwise it does not belong in this file list.
            path = path.relative_to(self.base)
        return super(FileListing, self).add(path, overwrite, **kwargs)
    
    def remove(self, path):
        """
        Remove the item at the relative or absolute path `path` from this file
        listing and return the item.  If no such item is found (including an
        absolute path that does not descend from `self.base`), return None.
        
        See the documentation for `Container.remove` for more details.
        
        """
        path = Path(path)
        if path.is_absolute:
            # This is an absolute path.  Ensure that `path` descends from
            # `self.base`, otherwise it does not belong in this file list.
            path = path.relative_to(self.base)
        return super(FileListing, self).remove(path)

    def get_partial(self, base=None, depth=-1):
        if base:
            base = Path(base)
            if not base.is_directory:
                raise RuntimeError("Base path must reference a directory.")
            elif base.is_relative:
                base = self.base.join(base)
            elif not base.descends_from(self.base):
                raise RuntimeError("Path does not descend from base.")
            listing = self.get(base)
        else:
            listing = self
            base = self.base
        
        partial = super(FileListing, listing).get_partial(depth)
        partial.base = base
        return partial

if __name__ == '__main__':
    import doctest
    doctest.testmod()