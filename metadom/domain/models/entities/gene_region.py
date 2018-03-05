from metadom.domain.repositories import MappingRepository
from metadom.domain.data_generation.mapping.Gene2ProteinMapping import convertListOfIntegerToRanges
import numpy as np

class FailedToConstructGeneRegion(Exception):
    pass

class RegioncDNALengthDoesNotEqualProteinLengthException(Exception):
    pass

class MalformedGeneRegionException(Exception):
    pass

class GeneRegion(object):
    """
    GeneRegion Model Entity
    Used for representation of (partial) gene regions for annotation purposes
    
    Variables
    name                      description
    chr                       str containing the chromosome number in form 'chr...'
    gene_name                 str containing the gene name of the region
    gencode_transcription_id  str containing the trancription id
    strand                    str containing the strand
    protein_region_start      int of start of the region 
    protein_region_stop       int of stop of the region
    protein_region_length     int representing the region length based on the amino acid sequence
    cDNA_region_length        int representing the region length based on the cDNA sequence
    regions                   list of regions
    """
    chr = str()
    gene_name = str()
    gencode_transcription_id = str()
    strand = str()
    protein_region_start = int()
    protein_region_stop = int()
    protein_region_length = int()
    cDNA_region_length = int()
    regions = []
    
    def __init__(self, _gene, _region_start=None, _region_stop=None):
        if _region_start is None:
            self.protein_region_start = 0
            
        if _region_stop is None:
            self.protein_region_stop = _gene.sequence_length
            
        # perform additional type checking
        if _region_stop < _region_start:
            raise MalformedGeneRegionException('_region_stop > _region_start')
        if _region_start < 0:
            raise MalformedGeneRegionException('_region_start < 0')
            
        # First set the fields that can directly be set from the _gene
        self.gene_name = _gene.gene_name
        self.gencode_transcription_id = _gene.gencode_transcription_id
        self.protein_region_length = _region_stop - _region_start
        self.strand = _gene.strand

        # Retrieve mappings from the database
        _mappings = MappingRepository.get_mappings_and_chromosomes_from_gene(_gene)

        # Check f everything went fine so far
        if len(_mappings) == 0:
            raise FailedToConstructGeneRegion("No proper mapping was found in the database, failed to initialize GeneRegion object")
        
        # Now generate the regions
        # create list that will be filled with all chromosomal positons of this region
        _chromosome_positions_in_region = []
        
        # keep track on uniprot residue positions
        _uniprot_positions = []
        _cDNA_positions = []
        
        # iterate over all cDNA positions
        for cDNA_position in sorted( _mappings.keys(), key=lambda x: int(x) ):
            _mapping = _mappings[cDNA_position]
            
            # test if we already set the chromosome
            if self.chr == str():
                self.chr = _mapping.chromosome
            else:
                # type check chromosome
                if self.chr !=  _mapping.chromosome:
                    raise MalformedGeneRegionException('Multiple chromosomes found for this gene')
            
            # ensure we have alignment here
            if _mapping.Mapping.uniprot_residue != '-':
                continue
            
            # test if this position falls within the region
            if self.protein_region_start <= _mapping.Mapping.uniprot_position < self.protein_region_stop:
                # Add the chromosomal position to the list
                _chromosome_positions_in_region.append(_mapping.position)
                _uniprot_positions.append(_mapping.Mapping.uniprot_position)
                _cDNA_positions.append(_mapping.Mapping.cDNA_position)
        
        # ensure that the region is fully covered
        if(self.protein_region_length != len(np.unique(_uniprot_positions))):
            raise RegioncDNALengthDoesNotEqualProteinLengthException("Attempted to recover chromosomal region, but the region was not perfectly aligned")
        
        # now add the cDNA region length
        self.cDNA_region_length = len(_cDNA_positions)

        # convert the chromosome to ranges
        self.regions = list(convertListOfIntegerToRanges(sorted(_chromosome_positions_in_region)))

    def __repr__(self):
        return "<GeneRegion(chr='%s', gene_name='%s', gencode_transcription_id='%s', protein_region_length='%s', cDNA_region_length='%s', strand='%s', number of chromosomal regions='%s')>" % (
                            self.chr, self.gene_name, self.gencode_transcription_id, self.protein_region_length, self.cDNA_region_length, self.strand, len(self.regions))