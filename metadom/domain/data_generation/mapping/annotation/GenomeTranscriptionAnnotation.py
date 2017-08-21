'''
Created on 18 jan. 2016

@author: Laurens van de Wiel
'''
from metadom.default_settings import EXAC_VCF_FILE, HGMD_VCF_FILE,\
    HGMD_CONSIDERED_CLASSES, EXAC_ACCEPTED_FILTERS, CLINVAR_CONSIDERED_CLINSIG,\
    CLINVAR_VCF_FILE
from metadom.controller.parsers.tabix import tabix_query, variant_coordinate_system
from metadom.controller.mapping.Gene2ProteinMapping import extract_gene_region,\
    RegioncDNALengthDoesNotEqualProteinLengthException
from metadom import _log

class NucleotideConversionException(Exception):
    pass

def annotateTranscriptWithClinvarData(gene_region):
    """
    Annotates variants found within the ClinVar dataset.
    Specific clinical signifcance level of interest is
    filtered (See INFO field CLNSIG)
    
    Additional fields:
    ID            ClinVar Variation ID
    
    ClinVar specific INFO fields:
    AF_ESP              allele frequencies from GO-ESP
    AF_EXAC             allele frequencies from ExAC
    AF_TGP              allele frequencies from TGP
    ALLELEID            The ClinVar Allele ID
    CLNDN               ClinVar's preferred disease name for the concept specified by disease identifiers in CLNDISDB
    CLNDNINCL           For included Variant : ClinVar's preferred disease name for the concept specified by disease identifiers in CLNDISDB
    CLNDISDB            Tag-value pairs of disease database name and identifier, e.g. OMIM:NNNNNN
    CLNDISDBINCL        For included Variant: Tag-value pairs of disease database name and identifier, e.g. OMIM:NNNNNN
    CLNHGVS             Top-level (primary assembly, alt, or patch) HGVS expression.
    CLNREVSTAT          ClinVar review status for the Variation ID
    CLNSIG              Clinical significance for this single variant
    CLNSIGINCL          Clinical significance for a haplotype or genotype that includes this variant. Reported as pairs of VariationID:clinical significance.
    CLNVC               Variant type
    CLNVCSO             Sequence Ontology id for variant type
    CLNVI               The variant's clinical sources reported as tag-value pairs of database and variant identifier
    DBVARID             nsv accessions from dbVar for the variant
    GENEINFO            Gene(s) for the variant reported as gene symbol:gene id. The gene symbol and id are delimited by a colon (:) and each pair is delimited by a vertical bar (|)
    MC                  comma separated list of molecular consequence in the form of Sequence Ontology ID|molecular_consequence
    ORIGIN              Allele origin. One or more of the following values may be added: 0 - unknown; 1 - germline; 2 - somatic; 4 - inherited; 8 - paternal; 16 - maternal; 32 - de-novo; 64 - biparental; 128 - uniparental; 256 - not-tested; 512 - tested-inconclusive; 1073741824 - other
    RS                  dbSNP ID (i.e. rs number)
    SSR                 Variant Suspect Reason Codes. One or more of the following values may be added: 0 - unspecified, 1 - Paralog, 2 - byEST, 4 - oldAlign, 8 - Para_EST, 16 - 1kg_failed, 1024 - other
    """
    for gene_sub_region in gene_region['regions']:
        for tabix_record in tabix_query(CLINVAR_VCF_FILE, gene_region['chr'][3:], gene_sub_region[0], gene_sub_region[1], variant_coordinate_system.one_based):
            for i, item in enumerate(tabix_record.ALT):
                clinvar_info = {"AF_ESP": None if "AF_ESP" not in tabix_record.INFO.keys() else tabix_record.INFO["AF_ESP"],
                            "AF_EXAC": None if "AF_EXAC" not in tabix_record.INFO.keys() else tabix_record.INFO["AF_EXAC"],
                            "AF_TGP": None if "AF_TGP" not in tabix_record.INFO.keys() else tabix_record.INFO["AF_TGP"],
                            "CLNDNINCL": None if "CLNDNINCL" not in tabix_record.INFO.keys() else tabix_record.INFO["CLNDNINCL"],
                            "CLNDISDBINCL": None if "CLNDISDBINCL" not in tabix_record.INFO.keys() else tabix_record.INFO["CLNDISDBINCL"],
                            "CLNSIGINCL": None if "CLNSIGINCL" not in tabix_record.INFO.keys() else tabix_record.INFO["CLNSIGINCL"],
                            "DBVARID": None if "DBVARID" not in tabix_record.INFO.keys() else tabix_record.INFO["DBVARID"],
                            "SSR": None if "SSR" not in tabix_record.INFO.keys() else tabix_record.INFO["SSR"],
                            "CLNVI": None if "CLNVI" not in tabix_record.INFO.keys() else tabix_record.INFO["CLNVI"],
                            "MC": None if "MC" not in tabix_record.INFO.keys() else tabix_record.INFO["MC"],
                            "RS": None if "RS" not in tabix_record.INFO.keys() else tabix_record.INFO["RS"],
                            "ORIGIN": None if "ORIGIN" not in tabix_record.INFO.keys() else tabix_record.INFO["ORIGIN"],
                            "CLNDN": None if "CLNDN" not in tabix_record.INFO.keys() else tabix_record.INFO["CLNDN"],
                            "CLNDISDB": None if "CLNDISDB" not in tabix_record.INFO.keys() else tabix_record.INFO["CLNDISDB"], 
                            "CLNSIG": None if "CLNSIG" not in tabix_record.INFO.keys() else tabix_record.INFO["CLNSIG"],
                            "GENEINFO": None if "GENEINFO" not in tabix_record.INFO.keys() else tabix_record.INFO["GENEINFO"],
                            "ALLELEID":tabix_record.INFO["ALLELEID"], "CLNHGVS":tabix_record.INFO["CLNHGVS"],
                            "CLNREVSTAT":tabix_record.INFO["CLNREVSTAT"], "CLNVC":tabix_record.INFO["CLNVC"],
                            "CLNVCSO":tabix_record.INFO["CLNVCSO"],"ID":tabix_record.ID}
            
                clinvar_record = {'CHROM': tabix_record.CHROM, 'POS': tabix_record.POS, 'REF':tabix_record.REF, 'ALT':item, 'INFO':clinvar_info}
                
                if not clinvar_record['INFO']['CLNSIG'] is None and\
                    len( clinvar_record['INFO']['CLNSIG'] ) == 1 and\
                    clinvar_record['INFO']['CLNSIG'][0] in CLINVAR_CONSIDERED_CLINSIG:
                    yield clinvar_record

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
        