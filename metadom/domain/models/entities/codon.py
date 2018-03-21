from metadom.domain.models.gene import Strand
from metadom.domain.services.helper_functions import convertListOfIntegerToRanges
class MalformedCodonException(Exception):
    pass

class Codon(object):
    """
    Codon Model Entity
    Used for a codon-representation of models.mapping.Mappings that make up a codon
    
    Variables
    name                       description
    mapping_ids                list the list of ids for the mappings associated to this codon
    gene_id                    int the gene id associated to this codon
    protein_id                 int the protein id associated to this codon
    strand                     Enum the strand represented as models.gene.Strand
    base_pair_representation   str the base pair representation of this codon (e.g. ATG)
    amino_acid_residue         str the amino acid residue of this codon
    amino_acid_position        int the amino acid position of this codon in the protein or gene translation
    chr                        str the chromosome
    regions                    tuple the range of chromosomal positions of this codon
    cDNA_position_range        tuple the range of cDNA positions of this codon
    """

    def unique_str_representation(self):
        return str(self.chr)+":"+str(self.regions)+"::("+str(self.strand)+")"

    def __init__(self, _mappings):
        self.mapping_ids = list()
        self.gene_id = int()
        self.protein_id = int()
        self.strand = str()
        self.base_pair_representation = str() 
        self.amino_acid_residue = str()
        self.amino_acid_position = int()
        self.chr = str()
        self.regions = tuple()  
        self.cDNA_position_range = tuple()
        
        # check the mappings cover exactly 3 mappings (thus represent a codon)
        if len(_mappings) != 3:
            raise MalformedCodonException("Malformed codon mapping: Expected exactly 3 mappings but got '"+str(len(_mappings))+"'.")
        
        # sort the mappings
        _mappings = sorted(_mappings, key=lambda k: k.codon_base_pair_position)
        self.mapping_ids = [_mappings[0].id, _mappings[1].id, _mappings[2].id, ]
        
        # double check the mapping for gene ids
        if not(_mappings[0].gene_id == _mappings[1].gene_id == _mappings[2].gene_id):
            raise MalformedCodonException("Malformed codon mapping: The gene ids are not the same for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for gene ids
        if not(_mappings[0].protein_id == _mappings[1].protein_id == _mappings[2].protein_id):
            raise MalformedCodonException("Malformed codon mapping: The protein ids are not the same for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for amino_acid_residue
        if not(_mappings[0].amino_acid_residue == _mappings[1].amino_acid_residue == _mappings[2].amino_acid_residue):
            raise MalformedCodonException("Malformed codon mapping: The encoded amino acid residue does not correspond for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for amino_acid_position
        if not(_mappings[0].amino_acid_position == _mappings[1].amino_acid_position == _mappings[2].amino_acid_position):
            raise MalformedCodonException("Malformed codon mapping: The encoded amino acid position does not correspond for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for chromosome
        if not(_mappings[0].chromosome == _mappings[1].chromosome == _mappings[2].chromosome):
            raise MalformedCodonException("Malformed codon mapping: The chromosome does not correspond for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for strand
        if not(_mappings[0].strand == _mappings[1].strand == _mappings[2].strand):
            raise MalformedCodonException("Malformed codon mapping: The strand does not correspond for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the cDNA positions for the mappins
        if not(_mappings[0].cDNA_position < _mappings[1].cDNA_position < _mappings[2].cDNA_position):
            raise MalformedCodonException("Malformed codon mapping: The cDNA positions do not agree follow in order for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # set the checked values
        self.gene_id = _mappings[0].gene_id
        self.protein_id = _mappings[0].protein_id
        self.strand = _mappings[0].strand
        self.amino_acid_residue = _mappings[0].amino_acid_residue
        self.amino_acid_position = _mappings[0].amino_acid_position
        self.chr = _mappings[0].chromosome
        self.cDNA_position_range = [_mappings[0].cDNA_position, _mappings[1].cDNA_position, _mappings[2].cDNA_position,]
        
        # check if the codon corresponds to the base pairs
        self.base_pair_representation = _mappings[0].base_pair+_mappings[1].base_pair+_mappings[2].base_pair
        if not(_mappings[0].codon == _mappings[1].codon == _mappings[2].codon == self.base_pair_representation):
            raise MalformedCodonException("Malformed codon mapping: The codons and base pairs of the mapping pair is malformed for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # Set the regions the same way as we set the regions in a gene_region
        self.regions = list(convertListOfIntegerToRanges(sorted([x.chromosome_position for x in _mappings])))
    
    def __repr__(self):
        return "<Codon(representation='%s', amino_acid_residue='%s', chr='%s', chr_positions='%s', strand='%s')>" % (
                            self.base_pair_representation, self.amino_acid_residue, self.chr, str(self.regions), self.strand )