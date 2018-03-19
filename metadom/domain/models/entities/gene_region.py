from metadom.domain.repositories import MappingRepository, ProteinRepository, InterproRepository
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
    protein_id                int identifier corresponding to the protein id in the database
    uniprot_ac                str representing the region's uniprot accession code
    uniprot_name              str representing the region's uniprot name
    interpro_domains          list containing interpro domains (models.interpro.Interpro)
    regions                   list of regions
    mappings_per_chromosome   dictionary of mappings per chromosome positions; {POS: models.mapping.Mapping}
    """
    chr = str()
    gene_name = str()
    gencode_transcription_id = str()
    strand = str()
    protein_region_start = int()
    protein_region_stop = int()
    protein_region_length = int()
    cDNA_region_length = int()
    protein_id = int()
    uniprot_ac = str()
    uniprot_name = str()
    interpro_domains = []
    regions = []
    mappings_per_chromosome = dict()
    
    # Source: http://stackoverflow.com/questions/4628333/converting-a-list-of-integers-into-range-in-python 
    def convertListOfIntegerToRanges(self, p):
        if len(p) > 0:
            q = sorted(p)
            i = 0
            for j in range(1,len(q)):
                if q[j] > 1+q[j-1]:
                    yield (q[i],q[j-1])
                    i = j
            yield (q[i], q[-1])
            
    def get_domains_for_position(self, position):
        return [domain for domain in self.interpro_domains if domain.uniprot_start-1 <= position <= domain.uniprot_stop]
            
    def __init__(self, _gene, _region_start=None, _region_stop=None):
        if _region_start is None or _region_start < 0:
            self.protein_region_start = 0
            
        if _region_stop is None or _region_stop > _gene.sequence_length:
            self.protein_region_stop = _gene.sequence_length
            
        # perform additional type checking
        if self.protein_region_stop < self.protein_region_start:
            raise MalformedGeneRegionException("For transcript '"+str(self.gencode_transcription_id)+
                                              "': attempted to build a gene region where_region_stop < _region_start")
            
        # First set the fields that can directly be set from the _gene
        self.gene_name = _gene.gene_name
        self.gencode_transcription_id = _gene.gencode_transcription_id
        self.protein_region_length = self.protein_region_stop - self.protein_region_start
        self.strand = _gene.strand
        
        
        # retrieve the protein id
        _protein = ProteinRepository.retrieve_protein(_gene.protein_id)
        
        # set the uniprot ac and name
        self.protein_id = _protein.id
        self.uniprot_ac = _protein.uniprot_ac
        self.uniprot_name = _protein.uniprot_name
        self.interpro_domains = InterproRepository.get_domains_for_protein(self.protein_id)
        
        # Retrieve mappings from the database
        _mappings = {x.cDNA_position:x for x in MappingRepository.get_mappings_for_gene(_gene)}

        # Check f everything went fine so far
        if len(_mappings) == 0:
            raise FailedToConstructGeneRegion("For transcript '"+str(self.gencode_transcription_id)+
                                              "': No proper mapping was found in the database,"+
                                              " failed to initialize GeneRegion object")
        
        # Now generate the regions
        # create list that will be filled with all chromosomal positons of this region
        _chromosome_positions_in_region = []
        
        # keep track on uniprot residue positions
        _uniprot_positions = []
        _cDNA_positions = []
        
        # iterate over all cDNA positions
        for cDNA_position in sorted( _mappings.keys(), key=lambda x: int(x) ):
            _mapping = _mappings[cDNA_position]
            
            # type check protein id
            if self.protein_id !=  _mapping.protein_id:
                raise MalformedGeneRegionException("For transcript '"+str(self.gencode_transcription_id)+
                                                   "': Found mappings for a single transcript aligned to multiple different proteins")


            # test if we already set the chromosome
            if self.chr == str():
                self.chr = _mapping.chromosome
            else:
                # type check chromosome
                if self.chr !=  _mapping.chromosome:
                    raise MalformedGeneRegionException("For transcript '"+str(self.gencode_transcription_id)+
                                                       "': Found alignments to multiple chromosomes")
            
            # ensure we have alignment here
            if _mapping.uniprot_residue == '-' or _mapping.uniprot_residue == '*':
                continue
            
            # test if this position falls within the region
            if self.protein_region_start <= _mapping.uniprot_position < self.protein_region_stop:
                # Add to the mapping to the mappings_per_chromosome
                self.mappings_per_chromosome[_mapping.chromosome_position] = _mapping
                
                # Add the chromosomal position to the list
                _chromosome_positions_in_region.append(_mapping.chromosome_position)
                _uniprot_positions.append(_mapping.uniprot_position)
                _cDNA_positions.append(_mapping.cDNA_position)
        
        # ensure that the region is fully covered
        if(self.protein_region_length != len(np.unique(_uniprot_positions))):
            raise RegioncDNALengthDoesNotEqualProteinLengthException("For transcript '"+str(self.gencode_transcription_id)+
                                                                     "': Attempted to recover chromosomal region, but the region was not"+
                                                                     " perfectly aligned, expected AA sequence length to be '"+str(self.protein_region_length)+"'"+
                                                                     ", but was '"+str(len(np.unique(_uniprot_positions)))+"'")
        
        # now add the cDNA region length
        self.cDNA_region_length = len(_cDNA_positions)

        # convert the chromosome to ranges
        self.regions = list(self.convertListOfIntegerToRanges(sorted(_chromosome_positions_in_region)))

    def __repr__(self):
        return "<GeneRegion(chr='%s', gene_name='%s', gencode_transcription_id='%s', protein_region_length='%s', cDNA_region_length='%s', strand='%s', number of chromosomal regions='%s')>" % (
                            self.chr, self.gene_name, self.gencode_transcription_id, self.protein_region_length, self.cDNA_region_length, self.strand, len(self.regions))