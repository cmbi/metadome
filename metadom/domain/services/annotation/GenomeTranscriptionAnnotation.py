from metadom.domain.models.gene import Strand

import logging

_log = logging.getLogger(__name__)

class NucleotideConversionException(Exception):
    pass    

def convertNucleotide(nucleotide):
    if nucleotide == 'A': return 'T'
    elif nucleotide == 'T': return 'A'
    elif nucleotide == 'C': return 'G'
    elif nucleotide == 'G': return 'C'
    else: raise NucleotideConversionException("Received nucleotide '"+str(nucleotide)+"', which could not be converted")

def annotateSNVs(annotateTranscriptFunction, gene_region):
    SNV_correct = 0
    SNV_incorrect = 0
    
    Annotation_mapping = {}

    annotation_data = annotateTranscriptFunction(gene_region)
    
    for annotation in annotation_data:
        # Check if we are dealing with a SNV
        if len(annotation['REF']) != 1: continue
        if len(annotation['ALT']) != 1: continue

        # retrieve the reference
        ref = str(annotation['REF'])
        # ensure we have correct strand, otherwise convert
        if gene_region.strand == Strand.minus: ref = convertNucleotide(annotation['REF'])
        
        # Check if the reference in the annotation_date is correct, compared to our transcript
        if gene_region.mappings_per_chromosome[annotation['POS']].base_pair == ref:
            SNV_correct = SNV_correct + 1
        else:
            SNV_incorrect = SNV_incorrect + 1
        
        # retrieve the alternate variation
        alt = annotation['ALT']
        
        # convert to string
        alt = str(alt)
        
        # ensure we have correct strand, otherwise convert
        if gene_region.strand == Strand.minus: alt = convertNucleotide(alt)
        
        # construct SNV entry
        SNV_entry = {key:annotation['INFO'][key] for key in annotation['INFO'].keys()}
        SNV_entry['REF'] = ref
        SNV_entry['ALT'] = alt
        SNV_entry['CHROM'] = annotation['CHROM']
        SNV_entry['POS'] = annotation['POS']
        
        # Genome key
        genomic_pos = int(annotation['POS'])
        
        # Annotate
        if genomic_pos not in Annotation_mapping.keys():
            Annotation_mapping[genomic_pos] = []
        
        Annotation_mapping[genomic_pos].append(SNV_entry)
    
    if SNV_incorrect > 0:
        _log.error("SNV ERROR: "+str(SNV_incorrect)+' incorrect vs '+str(SNV_correct)+' correct')
    
    return Annotation_mapping
        