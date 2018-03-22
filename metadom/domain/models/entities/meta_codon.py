class MalformedAggregatedCodon(Exception):
    pass

class MetaCodon(object):
    """
    MetaCodon Model Entity
    Used for a meta-codon representation of aggregated of models.entities.codon.Codon
    
    Variables
    name                       description
    chr                        str the chromosome
    regions                    tuple the range of chromosomal positions of this codon
    strand                     Enum the strand represented as models.gene.Strand
    amino_acid_residue         str the amino acid residue of this codon
    base_pair_representation   str the base pair representation of this codon (e.g. ATG)
    unique_str_representation  str unique string representation of the chromosomal region of this codon
    codon_aggregate            dict containing the duplicate chromosomal regions sorted as:
                                {codon.gene_id: 
                                    {'mapping_ids' : codon.mapping_ids,
                                     'protein_id' : codon.protein_id,
                                     'amino_acid_position': codon.amino_acid_position,
                                     'cDNA_position_range' : codon.cDNA_position_range,
                                    }
                                }
    """
    
    def __init__(self, codons):
        self.chr = str()
        self.regions = tuple() 
        self.strand = str() 
        self.amino_acid_residue = str() 
        self.base_pair_representation = str() 
        self.unique_str_representation = str()
        self.codon_aggregate = dict()
        
        # ensure codons is not empty
        if len(codons) == 0:
            raise MalformedAggregatedCodon('No codons were present in the input, no aggregate codon could be made')
        
        for codon in codons:
            if self.unique_str_representation == str():
                # current meta_codon has not yet been set
                self.chr = codon.chr
                self.regions = codon.regions 
                self.strand = codon.strand 
                self.base_pair_representation = codon.base_pair_representation 
                self.amino_acid_residue = codon.amino_acid_residue 
                self.unique_str_representation = codon.unique_str_representation()
            
            if not codon.unique_str_representation() == self.unique_str_representation:
                raise MalformedAggregatedCodon("The unique string representation of the codon's chromosomal region did not match all presented codons."+
                                               +" Expected '"+str(self.unique_str_representation)+"', but was '"+str(codon.unique_str_representation())+"'")
            
            if codon.gene_id in self.codon_aggregate.keys():
                raise MalformedAggregatedCodon("Duplicate codons of the same gene transcript '"+str(codon.gene_id)+"' received")
            
            self.codon_aggregate[codon.gene_id] = codon
    
    def __repr__(self):
        return "<MetaCodon(representation='%s', amino_acid_residue='%s', chr='%s', chr_positions='%s', strand='%s', aggregated_codons='%s')>" % (
                            self.base_pair_representation, self.amino_acid_residue, self.chr, str(self.regions), self.strand, str(len(self.codon_aggregate)))