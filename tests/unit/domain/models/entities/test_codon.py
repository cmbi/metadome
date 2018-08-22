import unittest

from metadome.domain.models.entities.codon import Codon

class mock_Mapping(object):
    strand = '+'
    amino_acid_position = 125
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
    
    def test_init_with_mapping(self):
        _transcript =  'test_transcript'
        _protein_ac =  'test_test_protein_ac'
        _codon_repr = 'CTT'
        _residue = 'L'
        _chromosome_position_base_pair_one = 231
        _chromosome_position_base_pair_two = 232
        _chromosome_position_base_pair_three = 233
        
        
        _mappings = []
        _mappings.append(mock_Mapping(id=1, base_pair='C', codon=_codon_repr, codon_base_pair_position=0, amino_acid_residue=_residue, cDNA_position=1, chromosome_position=_chromosome_position_base_pair_one))
        _mappings.append(mock_Mapping(id=2, base_pair='T', codon=_codon_repr, codon_base_pair_position=1, amino_acid_residue=_residue, cDNA_position=2, chromosome_position=_chromosome_position_base_pair_two))
        _mappings.append(mock_Mapping(id=3, base_pair='T', codon=_codon_repr, codon_base_pair_position=2, amino_acid_residue=_residue, cDNA_position=3, chromosome_position=_chromosome_position_base_pair_three))
         
        # Create the Codon
        codon = Codon(_mappings=_mappings, _gencode_transcription_id=_transcript, _uniprot_ac=_protein_ac)
        
        self.assertTrue(codon.three_letter_amino_acid_residue() == 'Leu')
        self.assertTrue(codon.gencode_transcription_id == _transcript)
        self.assertTrue(codon.uniprot_ac == _protein_ac)
        self.assertTrue(codon.strand == mock_Mapping.strand)
        self.assertTrue(codon.base_pair_representation == _codon_repr) 
        self.assertTrue(codon.amino_acid_residue == _residue)
        self.assertTrue(codon.amino_acid_position == mock_Mapping.amino_acid_position)
        self.assertTrue(codon.chr == mock_Mapping.chromosome)
        self.assertTrue(codon.chromosome_position_base_pair_one == _chromosome_position_base_pair_one)
        self.assertTrue(codon.chromosome_position_base_pair_two == _chromosome_position_base_pair_two)
        self.assertTrue(codon.chromosome_position_base_pair_three == _chromosome_position_base_pair_three)

        
    def test_three_letter_amino_acid_residue_selenocysteine(self):
        _mappings = []
        _mappings.append(mock_Mapping(id=1, base_pair='T', codon='TGA', codon_base_pair_position=0, amino_acid_residue='U', cDNA_position=1, chromosome_position=1))
        _mappings.append(mock_Mapping(id=2, base_pair='G', codon='TGA', codon_base_pair_position=1, amino_acid_residue='U', cDNA_position=2, chromosome_position=2))
        _mappings.append(mock_Mapping(id=3, base_pair='A', codon='TGA', codon_base_pair_position=2, amino_acid_residue='U', cDNA_position=3, chromosome_position=3))
         
        # Create the Codon
        codon = Codon(_mappings, 'test_transcript', 'test_protein_ac')
         
        self.assertTrue(codon.three_letter_amino_acid_residue() == 'Sec')
        
    def test_three_letter_amino_acid_residue_pyrrolysine(self):

        _mappings = []
        _mappings.append(mock_Mapping(id=1, base_pair='T', codon='TAG', codon_base_pair_position=0, amino_acid_residue='U', cDNA_position=1, chromosome_position=1))
        _mappings.append(mock_Mapping(id=2, base_pair='A', codon='TAG', codon_base_pair_position=1, amino_acid_residue='U', cDNA_position=2, chromosome_position=2))
        _mappings.append(mock_Mapping(id=3, base_pair='G', codon='TAG', codon_base_pair_position=2, amino_acid_residue='U', cDNA_position=3, chromosome_position=3))
         
        # Create the Codon
        codon = Codon(_mappings, 'test_transcript', 'test_protein_ac')
         
        self.assertTrue(codon.three_letter_amino_acid_residue() == 'Sec')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()