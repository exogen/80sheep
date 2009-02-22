#!/usr/bin/env python
import os
import unittest
from libsheep.filelist import FileListing, File, Directory, Path

EXAMPLE_FILENAME = 'resources/example_filelist.xml'
EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), EXAMPLE_FILENAME)

class TestFileListingIO(unittest.TestCase):
    def setUp(self):
        listing = FileListing('mycid', '/')
        listing.add('/share/')
        listing.add('/share/ADC.txt', size=154112)
        listing.add('/share/DC++ Prerelease/')
        listing.add('/share/DC++ Prerelease/DCPlusPlus.pdb', size=17648640)
        listing.add('/share/DC++ Prerelease/DCPlusPlus.exe', size=946176)
        listing.add('/share2/', incomplete=True)
        self.example_listing = listing
    
    def test_create_from_filename(self):
        listing = FileListing.from_file(EXAMPLE_PATH)
        self._test_example_listing(listing)
    
    def test_create_from_file_obj(self):
        listing = FileListing.from_file(open(EXAMPLE_PATH, 'r'))
        self._test_example_listing(listing)
    
    def test_create_from_string(self):
        listing = FileListing.from_string(open(EXAMPLE_PATH, 'r').read())
        self._test_example_listing(listing)
    
    def test_round_trip_compares_equal(self):
        listing_a = FileListing.from_file(EXAMPLE_PATH)
        a_serialized = listing_a.serialize()
        listing_b = FileListing.from_string(a_serialized)
        self.assertEquals(listing_a, listing_b)
    
    def _test_example_listing(self, listing):
        self.assertTrue(isinstance(listing, FileListing))
        self.assertTrue('share' in listing.contents)
        self.assertEquals(listing, self.example_listing)

class TestFileListingModification(unittest.TestCase):
    def setUp(self):
        self.listing = FileListing('mycid', '/share/')
    
    def test_add_file_returns_file(self):
        added_file = self.listing.add('a.txt')
        self.assertTrue(isinstance(added_file, File))
        self.assertTrue('a.txt' in self.listing.contents)
        self.assertEquals(self.listing.contents['a.txt'], added_file)
    
    def test_add_directory_returns_directory(self):
        added_dir = self.listing.add('a/')
        self.assertTrue(isinstance(added_dir, Directory))
        self.assertTrue('a' in self.listing.contents)
        self.assertEquals(self.listing.contents['a'], added_dir)
    
    def test_add_absolute_path_must_descend_from_base(self):
        self.assertRaises(RuntimeError, self.listing.add, '/a.txt')
    
    def test_add_does_not_overwrite(self):
        added_a = self.listing.add('a.txt')
        added_b = self.listing.add('a.txt')
        self.assertTrue(added_a is added_b)
    
    def test_add_file_has_no_size(self):
        added_a = self.listing.add('a.txt')
        self.assertEquals(added_a.size, None)
    
    def test_add_directory_is_complete(self):
        added_a = self.listing.add('a/')
        self.assertEquals(added_a.incomplete, False)
    
    def test_add_kwargs_become_attributes(self):
        added_a = self.listing.add('a.txt', size=123)
        added_b = self.listing.add('b/', incomplete=True)
        self.assertEquals(added_a.size, 123)
        self.assertEquals(added_b.incomplete, True)
    
    def test_intermediate_directories_created(self):
        self.listing.add('a/b/c.txt')
        dir_a = self.listing.contents['a']
        dir_b = dir_a.contents['b']
        self.assertTrue(isinstance(dir_a, Directory))
        self.assertTrue(isinstance(dir_b, Directory))
    
    def test_remove_returns_item(self):
        added_a = self.listing.add('a.txt')
        removed_a = self.listing.remove('a.txt')
        self.assertTrue(added_a is removed_a)
        added_b = self.listing.add('/share/a/b/')
        removed_b = self.listing.remove('/share/a/b')
        self.assertTrue(added_b is removed_b)
    
    def test_remove_nonexisting_returns_none(self):
        removed_a = self.listing.remove('a.txt')
        self.assertTrue(removed_a is None)
    
    def test_remove_dir_does_not_remove_file(self):
        added_c = self.listing.add('a/b/c')
        removed_c = self.listing.remove('a/b/c/')
        self.assertTrue(removed_c is None)

class TestPartialContainers(unittest.TestCase):
    def setUp(self):
        listing = FileListing('mycid', '/')
        listing.add('a/b/c/d.txt')
        listing.add('i/j/k.txt')
        listing.add('x/y/z/')
        self.listing = listing
    
    def test_partial_listing_same_base(self):
        partial = self.listing.get_partial(None)
        # Infinite depth, no difference!
        self.assertEquals(partial, self.listing)
        
        partial = self.listing.get_partial(None, 0)
    
    def test_partial_listing_with_base(self):
        # TODO
        pass


if __name__ == '__main__':
    unittest.main()
