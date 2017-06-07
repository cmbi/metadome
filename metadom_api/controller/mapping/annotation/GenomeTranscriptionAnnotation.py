'''
Created on 18 jan. 2016

@author: Laurens van de Wiel
'''
from metadom_api.default_settings import EXAC_VCF_FILE, HGMD_VCF_FILE,\
    HGMD_CONSIDERED_CLASSES, EXAC_ACCEPTED_FILTERS
from metadom_api.controller.parsers.tabix import tabix_query, variant_coordinate_system
from metadom_api.controller.mapping.Gene2ProteinMapping import extract_gene_region,\
    RegioncDNALengthDoesNotEqualProteinLengthException
import logging

_log = logging.getLogger(__name__)

class NucleotideConversionException(Exception):
    pass

def annotateTranscriptWithExacData(gene_region):
    """
    Annotates variants found within the ExAC dataset with specific FILTER settings.
        PASS : passed all variant filters imposed by ExAC, all such variants are considered real variants.
    """
    for gene_sub_region in gene_region['regions']:
        for tabix_record in tabix_query(EXAC_VCF_FILE, gene_region['chr'][3:], gene_sub_region[0], gene_sub_region[1], variant_coordinate_system.one_based):
            for i, item in enumerate(tabix_record.ALT):
                exac_filter = ''
                if len(tabix_record.FILTER) == 0:
                    exac_filter = 'PASS'
                else:
                    exac_filter = tabix_record.FILTER[0]
                
                if exac_filter in EXAC_ACCEPTED_FILTERS:
                    exac_record = {'CHROM': tabix_record.CHROM, 'POS': tabix_record.POS, 'FILTER':exac_filter, 'REF':tabix_record.REF, 'ALT':item, 'INFO':{'AC':tabix_record.INFO['AC'][i], 'AF':tabix_record.INFO['AF'][i], 'AN':tabix_record.INFO['AN']}}
                    yield exac_record
    
def annotateTranscriptWithHGMDData(gene_region):
    """
    Annotates variants found within the HGMD dataset with CLASS:
        DM: Disease-causing mutations are entered into HGMD where the authors of the corresponding report(s) have demonstrated that the reported mutation(s) are involved in conferring the associated clinical phenotype upon the individuals concerned.
        DM?: A probable/possible pathological mutation, reported to be pathogenic in the corresponding report, but where (1) the author has indicated that there may be some degree of uncertainty; (2) the HGMD curators believe greater interpretational caution is warranted; or (3) subsequent evidence has appeared in the literature which has called the putatively deleterious nature of the variant into question.
        DP: Disease-associated polymorphisms are entered into HGMD where there is evidence for a significant association with a disease/clinical phenotype along with additional evidence that the polymorphism is itself likely to be of functional relevance (e.g. as a consequence of genic/genomic location, evolutionary conservation, transcription factor binding potential, etc.), although there may be no direct evidence (e.g. from an expression study) of a functional effect.
        FP: Functional polymorphisms are included in HGMD where the reporting authors have shown that the polymorphism in question exerts a direct functional effect (e.g. by means of an in vitro reporter gene assay or alternatively by protein structure, function or expression studies), but with no disease association reported as yet.
        DFP: Disease-associated polymorphisms with supporting functional evidence meet both of the criteria in FP and DP that the polymorphism should not only be reported to be significantly associated with disease but should also display evidence of being of direct functional relevance.
        R: An entry retired from HGMD due to being found to have been erroneously included ab initio, or subject to correction in the literature resulting in the record becoming obsolete, merged or otherwise invalid.
    """
    for gene_sub_region in gene_region['regions']:
        for tabix_record in tabix_query(HGMD_VCF_FILE, gene_region['chr'][3:], gene_sub_region[0], gene_sub_region[1], variant_coordinate_system.one_based, encoding='utf-8'):
            for i, item in enumerate(tabix_record.ALT): 
                if tabix_record.INFO['CLASS'] in HGMD_CONSIDERED_CLASSES:
                    hgmd_info = {'CLASS':tabix_record.INFO['CLASS'], 'PHEN':tabix_record.INFO['PHEN'], 
                                  'PROT': None if 'PROT' not in tabix_record.INFO.keys() else tabix_record.INFO['PROT'], 
                                  'DNA': None if 'DNA' not in tabix_record.INFO.keys() else tabix_record.INFO['DNA'],
                                  'MUT': None if 'MUT' not in tabix_record.INFO.keys() else tabix_record.INFO['MUT'], 
                                  'GENE':tabix_record.INFO['GENE'], 'STRAND':tabix_record.INFO['STRAND']}
                    hgmd_record = {'CHROM': tabix_record.CHROM, 'POS': tabix_record.POS, 'REF':tabix_record.REF, 'ALT':item, 'INFO':hgmd_info}
                    yield hgmd_record      

def convertNucleotide(nucleotide):
    if nucleotide == 'A': return 'T'
    elif nucleotide == 'T': return 'A'
    elif nucleotide == 'C': return 'G'
    elif nucleotide == 'G': return 'C'
    else: raise NucleotideConversionException("Received nucleotide '"+str(nucleotide)+"', which could not be converted")

def annotateSNVs(annotateTranscriptFunction, gene_mapping, region=None):
    SNV_correct = 0
    SNV_incorrect = 0
    
    Annotation_mapping = {}
    # Add annotation_data
    if region is None:
        try:
            # use the full transcript as region
            region_start = 0
            region_stop = len(gene_mapping['uniprot']['sequence'])
            region = extract_gene_region(gene_mapping, region_start, region_stop)
        except (RegioncDNALengthDoesNotEqualProteinLengthException) as e:
            _log.error(e)
            return

    annotation_data = annotateTranscriptFunction(region)
    
    for annotation in annotation_data:
        # Check if we are dealing with a SNV
        if len(annotation['REF']) != 1: continue
        if len(annotation['ALT']) != 1: continue

        # retrieve the reference
        ref = str(annotation['REF'])
        # ensure we have correct strand, otherwise convert
        if gene_mapping['gene_transcription']['strand'] == '-': ref = convertNucleotide(annotation['REF'])
        
        # Genome key
        genomic_pos = 'chr'+annotation['CHROM']+':'+str(annotation['POS'])
        
        # Check if the reference in the annotation_date is correct, compared to our transcript
        if gene_mapping['GenomeMapping']['Genome'][genomic_pos]['allele'] == ref:
            SNV_correct = SNV_correct + 1
        else:
            SNV_incorrect = SNV_incorrect + 1
        
        # retrieve the alternate variation
        alt = annotation['ALT']
        
        # convert to string
        alt = str(alt)
        
        # ensure we have correct strand, otherwise convert
        if gene_mapping['gene_transcription']['strand'] == '-': alt = convertNucleotide(alt)
        
        # construct SNV entry
        SNV_entry = {key:annotation['INFO'][key] for key in annotation['INFO'].keys()}
        SNV_entry['REF'] = ref
        SNV_entry['ALT'] = alt
        
        # Annotate
        if genomic_pos not in Annotation_mapping.keys():
            Annotation_mapping[genomic_pos] = []
        
        Annotation_mapping[genomic_pos].append(SNV_entry)
    
    if SNV_incorrect > 0:
        _log.error("SNV ERROR: "+str(SNV_incorrect)+' incorrect vs '+str(SNV_correct)+' correct')
    
    return Annotation_mapping
        