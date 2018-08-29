from metadome.domain.models.entities.codon import Codon, MalformedCodonException
import enum

class MalformedVariantException(Exception):
    pass

class VariantType(enum.Enum):
    missense = 'missense'
    nonsense = 'nonsense'
    synonymous = 'synonymous'

class SingleNucleotideVariant(Codon):
    """
    SingleNucleotideVariant Model Entity
    Used for a single nucleotide variant representation of models.entities.Codon
    
    Extends the Codon class with the following variables
    name                                   description
    var_codon_position                     int the position in the codon corresponding to the variant (0,1,2)
    ref_nucleotide                         str the reference nucleotide at the var_codon_position
    alt_nucleotide                         str the alternative nucleotide at the var_codon_position
    alt_amino_acid_residue                 str the alternative amino acid residue of this variant
    variant_type                           Enum the variant type (i.e.: missense, synonymous, nonsense)    
    """

    def __init__(self, _gencode_transcription_id, _uniprot_ac, 
                             _strand, _base_pair_representation, 
                             _amino_acid_residue, _amino_acid_position, 
                             _chr, _chromosome_position_base_pair_one, 
                             _chromosome_position_base_pair_two, 
                             _chromosome_position_base_pair_three,
                             _cDNA_position_one, _cDNA_position_two,
                             _cDNA_position_three, 
                             _variant_type,
                             _alt_amino_acid_residue,
                             _ref_nucleotide,
                             _alt_nucleotide,
                             _var_codon_position):
        # Init the parent object
        super().__init__(_gencode_transcription_id=_gencode_transcription_id,
                         _uniprot_ac=_uniprot_ac, _strand=_strand, 
                         _base_pair_representation=_base_pair_representation, 
                         _amino_acid_residue=_amino_acid_residue, 
                         _amino_acid_position=_amino_acid_position, 
                         _chr=_chr, 
                         _chromosome_position_base_pair_one=_chromosome_position_base_pair_one, 
                         _chromosome_position_base_pair_two=_chromosome_position_base_pair_two, 
                         _chromosome_position_base_pair_three=_chromosome_position_base_pair_three,
                         _cDNA_position_one=_cDNA_position_one, 
                         _cDNA_position_two=_cDNA_position_two,
                         _cDNA_position_three=_cDNA_position_three)
        # Init the rest for SingleNucleotideVariant
        self.ref_nucleotide = str()
        self.alt_nucleotide = str()
        self.var_codon_position = int()
        self.variant_type = str()
        self.alt_amino_acid_residue = _alt_amino_acid_residue

        # start the type and rule checks
        if _ref_nucleotide == _alt_nucleotide:
            raise MalformedVariantException("No SNV could be made: found identical ref and alt nucleotides")
        if len(_ref_nucleotide) == len(_alt_nucleotide) == 1:
            self.ref_nucleotide = _ref_nucleotide
            self.alt_nucleotide = _alt_nucleotide
        else:
            raise MalformedVariantException("No SNV could be made: The ref '"+str(_ref_nucleotide)+"' and alt '"+str(_alt_nucleotide)+"' nucleotides should both have total length '1'")
        
        # double check that the codon position is indeed in range 0,1,2
        if 0 <= _var_codon_position <= 2:
            self.var_codon_position = _var_codon_position
        else:
            raise MalformedVariantException("No SNV could be made: _var_codon_position, indicating the variant in the basepair position in the codon should be 0, 1, or 2 but was '"+str(_var_codon_position)+"'")
        
        # check if the var position correspond to the ref nucleotide
        if self.base_pair_representation[self.var_codon_position] != self.ref_nucleotide:
            raise MalformedVariantException("No SNV could be made: the ref nucleoide '"+str(self.ref_nucleotide)+"' does not correspond to the var_codon_position '"+str(self.var_codon_position)+"' in the base_pair_representation '"+str(self.base_pair_representation)+"'")
         
        # check that the variant type is of missense, nonsense, synonymous
        if _variant_type == 'missense':
            self.variant_type = VariantType.missense
        elif _variant_type == 'synonymous':
            self.variant_type = VariantType.synonymous
        elif _variant_type == 'nonsense':
            self.variant_type = VariantType.nonsense
        else:
            raise MalformedVariantException('No SNV could be made: Variant type cold not be converted to domain.models.entities.SingleNucleotideVariant.VariantType(Enum) for provided: '+str(_variant_type))
    
    def toDict(self):
        # create the dictionary based on the codon
        _d = Codon.toDict(self)
        
        # Add the variables of SNV
        _d['ref_nucleotide'] = self.ref_nucleotide
        _d['alt_nucleotide'] = self.alt_nucleotide
        _d['var_codon_position'] = self.var_codon_position
        _d['variant_type'] = self.variant_type.value
        _d['alt_amino_acid_residue'] = self.alt_amino_acid_residue
        
        return _d
    
    @classmethod
    def initializeFromDict(cls, _d):
        try:
            # Double check the _codon is properly formatted
            _codon = Codon.initializeFromDict(_d)
            
            # initialize the other expected values from 
            _ref_nucleotide = _d['ref_nucleotide']
            _alt_nucleotide = _d['alt_nucleotide']
            _var_codon_position = _d['var_codon_position']
            _variant_type = _d['variant_type']
            _alt_amino_acid_residue  = _d['alt_amino_acid_residue']
            
            SNV = cls(_gencode_transcription_id=_codon.gencode_transcription_id,
                                    _uniprot_ac=_codon.uniprot_ac, _strand=_codon.strand.value,
                                    _base_pair_representation=_codon.base_pair_representation, 
                                    _amino_acid_residue=_codon.amino_acid_residue, 
                                    _amino_acid_position=_codon.amino_acid_position, 
                                    _chr=_codon.chr, 
                                    _chromosome_position_base_pair_one=_codon.chromosome_position_base_pair_one, 
                                    _chromosome_position_base_pair_two=_codon.chromosome_position_base_pair_two, 
                                    _chromosome_position_base_pair_three=_codon.chromosome_position_base_pair_three,
                                    _cDNA_position_one=_codon.cDNA_position_one, 
                                    _cDNA_position_two=_codon.cDNA_position_two, 
                                    _cDNA_position_three=_codon.cDNA_position_three,
                                    _variant_type=_variant_type, 
                                    _alt_amino_acid_residue='I', 
                                    _ref_nucleotide=_ref_nucleotide, 
                                    _alt_nucleotide=_alt_nucleotide,
                                    _var_codon_position=_var_codon_position)
            
            return SNV
        except MalformedCodonException as e:
            raise MalformedCodonException("Upon constructing SingleNucleotideVariant: Malformed codon from dict: KeyError with message: "+str(e))
        except KeyError as e:
            raise MalformedVariantException("Malformed variant from dict: KeyError with message: "+str(e))
    
    @classmethod
    def initializeFromMapping(cls, _mappings, _gencode_transcription_id, _uniprot_ac):
        raise NotImplementedError("The function "'initializeFromMapping'" is not supported for SingleNucleotideVariant class")     
    
    def __repr__(self):
        return "<SingleNucleotideVariant(chr='%s', chr_positions='%s', strand='%s', ref_codon='%s', ref_aa='%s',)>" % (
                            self.chr, str(self.regions), self.strand, self.base_pair_representation, self.amino_acid_residue)
