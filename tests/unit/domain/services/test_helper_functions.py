import unittest
from metadom.domain.services.helper_functions import create_sliding_window, convertListOfIntegerToRanges

class TestHelperFunctions(unittest.TestCase):

    def test_convertListOfIntegerToRanges(self):
        self.assertEqual([x for x in convertListOfIntegerToRanges([0])], [(0, 0)])
        self.assertEqual([x for x in convertListOfIntegerToRanges([0,1])], [(0, 1)])
        self.assertEqual([x for x in convertListOfIntegerToRanges([0,2])], [(0, 0), (2, 2)])
        self.assertEqual([x for x in convertListOfIntegerToRanges([0,1,2,4,5,6])], [(0, 2), (4, 6)])
        

    def test_create_sliding_windowName(self):
        self.assertEqual(create_sliding_window(-1, 0), [])
        self.assertEqual(create_sliding_window(0, 0), [])
        
        self.assertEqual(create_sliding_window(5, -1), 
                         [{'sw_coverage': 1.0, 'sw_range': range(0, 0)},
                          {'sw_coverage': 1.0, 'sw_range': range(1, 1)},
                          {'sw_coverage': 1.0, 'sw_range': range(2, 2)},
                          {'sw_coverage': 1.0, 'sw_range': range(3, 3)},
                          {'sw_coverage': 1.0, 'sw_range': range(4, 4)}])
        
        self.assertEqual(create_sliding_window(5, 0), 
                         [{'sw_coverage': 1.0, 'sw_range': range(0, 0)},
                          {'sw_coverage': 1.0, 'sw_range': range(1, 1)},
                          {'sw_coverage': 1.0, 'sw_range': range(2, 2)},
                          {'sw_coverage': 1.0, 'sw_range': range(3, 3)},
                          {'sw_coverage': 1.0, 'sw_range': range(4, 4)}])

        self.assertEqual(create_sliding_window(5, 1), 
                         [{'sw_coverage': 0.6666666666666666, 'sw_range': range(0, 2)},
                          {'sw_coverage': 1.0, 'sw_range': range(0, 3)},
                          {'sw_coverage': 1.0, 'sw_range': range(1, 4)},
                          {'sw_coverage': 1.0, 'sw_range': range(2, 5)},
                          {'sw_coverage': 0.6666666666666666, 'sw_range': range(3, 5)}])
        
        self.assertEqual(create_sliding_window(5, 2), 
                         [{'sw_coverage': 0.6, 'sw_range': range(0, 3)}, 
                          {'sw_coverage': 0.8, 'sw_range': range(0, 4)}, 
                          {'sw_coverage': 1.0, 'sw_range': range(0, 5)}, 
                          {'sw_coverage': 0.8, 'sw_range': range(1, 5)}, 
                          {'sw_coverage': 0.6, 'sw_range': range(2, 5)}])
        
        self.assertEqual(create_sliding_window(5, 5), 
                         [{'sw_coverage': 0.45454545454545453, 'sw_range': range(0, 5)},
                          {'sw_coverage': 0.45454545454545453, 'sw_range': range(0, 5)},
                          {'sw_coverage': 0.45454545454545453, 'sw_range': range(0, 5)},
                          {'sw_coverage': 0.45454545454545453, 'sw_range': range(0, 5)},
                          {'sw_coverage': 0.45454545454545453, 'sw_range': range(0, 5)}])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()