import unittest

from metadome.domain.models.entities.codon import Codon

class mock_Mapping(object):
    strand = '+'
    amino_acid_position = 1
    chromosome = 'chr1'
    gene_id = 1
    protein_id = 1
    
    def __init__(self, id, base_pair, codon, codon_base_pair_position,
                 cDNA_position, amino_acid_residue, chromosome_position):
        self.id = id
        self.base_pair = base_pair
        self.codon = codon
        self.codon_base_pair_position = codon_base_pair_position
        self.cDNA_position = cDNA_position
        self.amino_acid_residue = amino_acid_residue
        self.chromosome_position = chromosome_position


# @mock.patch("flask_sqlalchemy.SignallingSession", autospec=True)
class Test_codon(unittest.TestCase):
    

        
    def test_three_letter_amino_acid_residue_selenocysteine(self):
        _mappings = []
        _mappings.append(mock_Mapping(id=1, base_pair='T', codon='TGA', codon_base_pair_position=0, amino_acid_residue='U', cDNA_position=1, chromosome_position=1))
        _mappings.append(mock_Mapping(id=2, base_pair='G', codon='TGA', codon_base_pair_position=1, amino_acid_residue='U', cDNA_position=2, chromosome_position=2))
        _mappings.append(mock_Mapping(id=3, base_pair='A', codon='TGA', codon_base_pair_position=2, amino_acid_residue='U', cDNA_position=3, chromosome_position=3))
         
        # Create the Codon
        codon = Codon(_mappings)
         
        self.assertTrue(codon.three_letter_amino_acid_residue() == 'Sec')
        
    def test_three_letter_amino_acid_residue_pyrrolysine(self):

        _mappings = []
        _mappings.append(mock_Mapping(id=1, base_pair='T', codon='TAG', codon_base_pair_position=0, amino_acid_residue='U', cDNA_position=1, chromosome_position=1))
        _mappings.append(mock_Mapping(id=2, base_pair='A', codon='TAG', codon_base_pair_position=1, amino_acid_residue='U', cDNA_position=2, chromosome_position=2))
        _mappings.append(mock_Mapping(id=3, base_pair='G', codon='TAG', codon_base_pair_position=2, amino_acid_residue='U', cDNA_position=3, chromosome_position=3))
         
        # Create the Codon
        codon = Codon(_mappings)
         
        self.assertTrue(codon.three_letter_amino_acid_residue() == 'Sec')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()