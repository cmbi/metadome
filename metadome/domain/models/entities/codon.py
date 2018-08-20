from metadome.domain.services.helper_functions import convertListOfIntegerToRanges, list_of_stringified_of_ranges
from Bio.Data.IUPACData import protein_letters_1to3
from metadome.domain.services.computation.codon_computations import interpret_alt_codon, residue_variant_type
from Bio.Seq import translate

class MalformedCodonException(Exception):
    pass

class Codon(object):
    """
    Codon Model Entity
    Used for a codon-representation of models.mapping.Mappings that make up a codon
    
    Variables
    name                       description
    mappings                   list of the mapping objects for these locations
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
    
    def retrieve_mappings_per_chromosome(self):
        """Returns the mappings for this codon per chromosome position"""
        mappings_per_chromosome = dict()
        for mapping in self.mappings:
            mappings_per_chromosome[mapping.chromosome_position] = mapping
        return mappings_per_chromosome
    
    def interpret_SNV_type(self, position, var_nucleotide):
        """Interprets the new codon, residue and type of a SNV"""
        codon_pos = self.retrieve_mappings_per_chromosome()[position].codon_base_pair_position
        
        alt_codon = interpret_alt_codon(self.base_pair_representation, codon_pos, var_nucleotide)
        alt_residue = translate(alt_codon)
        var_type = residue_variant_type(self.amino_acid_residue, alt_residue)
        
        if not var_type == 'nonsense':
            alt_residue_triplet = protein_letters_1to3[alt_residue]
        else:
            alt_residue_triplet = alt_residue
        
        return alt_codon, alt_residue, alt_residue_triplet, var_type
    
    def three_letter_amino_acid_residue(self):
        """Returns a three letter representation of the amino acid residue for this codon"""
        # Check if this is a Pyrrolysine
        if self.amino_acid_residue == 'O':
            return 'Pyl'
        # Check if this is a Selenocysteine
        if self.amino_acid_residue == 'U':
            return 'Sec'
        # Return one of the 20 amino acid residues
        return protein_letters_1to3[self.amino_acid_residue];
    
    def pretty_print_cDNA_region(self):
        return "c."+str(self.cDNA_position_range[0])+"-"+str(self.cDNA_position_range[2])
    
    def pretty_print_chr_region(self):
        _stringified_list = list_of_stringified_of_ranges(self.regions)
        return "".join("g."+_stringified_list[i] if i+1 == len(_stringified_list) else "g."+_stringified_list[i]+", " for i in range(len(_stringified_list)))

    def __init__(self, _mappings):
        self.mappings = list()
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
        self.mappings = sorted(_mappings, key=lambda k: k.codon_base_pair_position)
        self.mapping_ids = [self.mappings[0].id, self.mappings[1].id, self.mappings[2].id, ]
        
        # double check the mapping for gene ids
        if not(self.mappings[0].gene_id == self.mappings[1].gene_id == self.mappings[2].gene_id):
            raise MalformedCodonException("Malformed codon mapping: The gene ids are not the same for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for gene ids
        if not(self.mappings[0].protein_id == self.mappings[1].protein_id == self.mappings[2].protein_id):
            raise MalformedCodonException("Malformed codon mapping: The protein ids are not the same for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for amino_acid_residue
        if not(self.mappings[0].amino_acid_residue == self.mappings[1].amino_acid_residue == self.mappings[2].amino_acid_residue):
            raise MalformedCodonException("Malformed codon mapping: The encoded amino acid residue does not correspond for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for amino_acid_position
        if not(self.mappings[0].amino_acid_position == self.mappings[1].amino_acid_position == self.mappings[2].amino_acid_position):
            raise MalformedCodonException("Malformed codon mapping: The encoded amino acid position does not correspond for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for chromosome
        if not(self.mappings[0].chromosome == self.mappings[1].chromosome == self.mappings[2].chromosome):
            raise MalformedCodonException("Malformed codon mapping: The chromosome does not correspond for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the mapping for strand
        if not(self.mappings[0].strand == self.mappings[1].strand == self.mappings[2].strand):
            raise MalformedCodonException("Malformed codon mapping: The strand does not correspond for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # double check the cDNA positions for the mappins
        if not(self.mappings[0].cDNA_position < self.mappings[1].cDNA_position < self.mappings[2].cDNA_position):
            raise MalformedCodonException("Malformed codon mapping: The cDNA positions do not agree follow in order for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # set the checked values
        self.gene_id = self.mappings[0].gene_id
        self.protein_id = self.mappings[0].protein_id
        self.strand = self.mappings[0].strand
        self.amino_acid_residue = self.mappings[0].amino_acid_residue
        self.amino_acid_position = self.mappings[0].amino_acid_position
        self.chr = self.mappings[0].chromosome
        self.cDNA_position_range = [self.mappings[0].cDNA_position, self.mappings[1].cDNA_position, self.mappings[2].cDNA_position,]
        
        # check if the codon corresponds to the base pairs
        self.base_pair_representation = self.mappings[0].base_pair+self.mappings[1].base_pair+self.mappings[2].base_pair
        if not(self.mappings[0].codon == self.mappings[1].codon == self.mappings[2].codon == self.base_pair_representation):
            raise MalformedCodonException("Malformed codon mapping: The codons and base pairs of the mapping pair is malformed for mapping ids: '"+str(self.mapping_ids)+"'.")
        
        # Set the regions the same way as we set the regions in a gene_region
        self.regions = list(convertListOfIntegerToRanges(sorted([x.chromosome_position for x in self.mappings])))
    
    def __repr__(self):
        return "<Codon(representation='%s', amino_acid_residue='%s', chr='%s', chr_positions='%s', strand='%s')>" % (
                            self.base_pair_representation, self.amino_acid_residue, self.chr, str(self.regions), self.strand )