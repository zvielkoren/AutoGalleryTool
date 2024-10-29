import unittest

from src.modules.sorting_files import FileSorter


class TestSortingFile(unittest.TestCase):
    def setUp(self):
       self.sorter = FileSorter("source_dir", "destination_dir")



def test_sort_files(self):
    # Test the sort_files method
    self.sorter.sort_files()
    # Add assertions to check if files are sorted correctly





if __name__ == '__main__':
    unittest.main()
