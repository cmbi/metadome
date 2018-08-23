import unittest
from metadome.domain.models.entities.meta_domain import MetaDomain,\
    UnsupportedMetaDomainIdentifier

class Test_meta_domain(unittest.TestCase):
    
    def test_invalid_domain_id(self):
        with self.assertRaises(UnsupportedMetaDomainIdentifier):
            MetaDomain.initializeFromDomainID('PFTEST')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()