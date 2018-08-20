'''
Created on Aug 20, 2018

@author: laurens
'''
import unittest
from metadome.domain.models.entities.codon import Codon
from metadome.domain.models.mapping import Mapping


class Test_codon(unittest.TestCase):
    
    def test_three_letter_amino_acid_residue_selenocysteine(self):
        _mappings = []
        _mappings.append(Mapping(base_pair='T', codon='TGA', codon_base_pair_position=0, amino_acid_residue='U', cDNA_position=1, chromosome_position=1))
        _mappings.append(Mapping(base_pair='G', codon='TGA', codon_base_pair_position=1, amino_acid_residue='U', cDNA_position=2, chromosome_position=2))
        _mappings.append(Mapping(base_pair='A', codon='TGA', codon_base_pair_position=2, amino_acid_residue='U', cDNA_position=3, chromosome_position=3))
        
        # Create the Codon
        codon = Codon(_mappings)
        
        self.assertTrue(codon.three_letter_amino_acid_residue() == 'Sec')
        
    def test_three_letter_amino_acid_residue_pyrrolysine(self):
        _mappings = []
        _mappings.append(Mapping(base_pair='T', codon='TAG', codon_base_pair_position=0, amino_acid_residue='U', cDNA_position=1, chromosome_position=1))
        _mappings.append(Mapping(base_pair='A', codon='TAG', codon_base_pair_position=1, amino_acid_residue='U', cDNA_position=2, chromosome_position=2))
        _mappings.append(Mapping(base_pair='G', codon='TAG', codon_base_pair_position=2, amino_acid_residue='U', cDNA_position=3, chromosome_position=3))
        
        # Create the Codon
        codon = Codon(_mappings)
        
        self.assertTrue(codon.three_letter_amino_acid_residue() == 'Sec')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()