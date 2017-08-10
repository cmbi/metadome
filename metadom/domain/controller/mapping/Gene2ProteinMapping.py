'''
Created on May 6, 2016

@author: laurens
'''
from metadom.controller.mapping.Protein2ProteinMapping import createMappingOfAASequenceToAASequence,\
    map_single_residue
from metadom.controller.wrappers.pdb import getRefseqForPDBfile,\
    retrieveAtomicStructureSequence, retrieveAtomicStructureMapping,\
    AtomicSequenceIDMappingFailedException
import numpy as np
import logging

_log = logging.getLogger(__name__)

class RegioncDNALengthDoesNotEqualProteinLengthException(Exception):
    pass

# Source: http://stackoverflow.com/questions/4628333/converting-a-list-of-integers-into-range-in-python 
def convertListOfIntegerToRanges(p):
    q = sorted(p)
    i = 0
    for j in range(1,len(q)):
        if q[j] > 1+q[j-1]:
            yield (q[i],q[j-1])
            i = j
    yield (q[i], q[-1])

def createMappingOfGeneTranscriptionToTranslationToProtein(gene_report):
    # Retrieve the gene transcription
    transcription = gene_report["gene_transcription"]
    # Retrieve the amino acid sequence according to the translation
    gene_protein_translation_sequence = gene_report["translation_used"]['sequence']
    # Retrieve the canonical uniprot sequence
    canonical_protein_sequence = gene_report["uniprot"]["sequence"]
    # nucleotide sequence containing of the CDS
    coding_sequence = transcription['coding-sequence']
    # CDS for nucleotide positions
    cds =  transcription['CDS_annotation']
    
    if not ("pdb_seqres_used" in gene_report.keys()) \
        or not("measured_structure_sequence" in gene_report.keys()) \
        or gene_report["pdb_seqres_used"] is None \
        or gene_report["measured_structure_sequence"] is None: has_structure = False
    else:
        has_structure = True
        
    # check if there are multiple chromosomal positions
    chr_in_cds = list(set([cd.seqid for cd in cds]))
    if len(chr_in_cds) > 1:
        _log.warning('Found multiple chromosomes in coding sequence: '+str(chr_in_cds)+', using only '+str(chr_in_cds[0])+', this may indicate pseudoautosomal genes')
    
    # Create mapping between Gene and cDNA
    cDNA_pos = 0
    currentChr = ''
    GenomeMapping = {"Genome":dict(), "cDNA":dict()}
    for cd in cds:
        if currentChr == '': currentChr = cd.seqid # set it as the first
        elif not(cd.seqid == currentChr):
            _log.warning('Coding sequence with '+str(cd.seqid)+' does not match on chromosome '+str(currentChr)+', skipping this coding sequence...')
            continue # skip this Chromosome
        if cd.strand == '-':
            custom_range = range(cd.end, cd.start-1, -1)
        else:
            custom_range = range(cd.start, cd.end+1)
        for i in custom_range:
            allele = coding_sequence[cDNA_pos]
            GenomePos = cd.seqid+':'+str(i)
            cDNA_pos = cDNA_pos+1
            
            GenomeMapping['Genome'][GenomePos] = {'cDNA':cDNA_pos, 'allele':allele}
            GenomeMapping['cDNA'][cDNA_pos] = {'Genome':GenomePos, 'allele':allele}
    
    # ensure we have the stop codon at the end of the translation sequence
    gene_protein_translation_sequence+='*'
    
    # align cDNA sequence with uniprot canonical sequence
    translation_to_uniprot_mapping  = createMappingOfAASequenceToAASequence(gene_protein_translation_sequence, canonical_protein_sequence)
    
    PDBStructureMappings = []
    if has_structure:
        # Create a mapping for each of the found structures and chains
        for matched_pdb_structure in gene_report['pdb_seqres_matches']:
            # Retrieve the seqres sequence of the pdb file
            matched_pdb_structure['sequence'] = getRefseqForPDBfile(matched_pdb_structure['pdb_id'], matched_pdb_structure["chain_id"])
            
            # Retrieve the measured structure sequence as found in the PDB file
            matched_pdb_structure['measured_structure_sequence'] = retrieveAtomicStructureSequence(matched_pdb_structure)
        
            # create a mapping from the gene translation to the PDB seqres 
            matched_pdb_structure['translation_to_seqres_mapping'] = createMappingOfAASequenceToAASequence(gene_protein_translation_sequence, matched_pdb_structure['sequence'])
            
            # create a mapping from the gene translation sequence and the measured structure sequence
            matched_pdb_structure['translation_to_structure_mapping'] = createMappingOfAASequenceToAASequence(gene_protein_translation_sequence, matched_pdb_structure['measured_structure_sequence'])
            
            try: 
                # create a mapping in order to interpret the sequence to structure mapping based on the atomic structure
                matched_pdb_structure['measured_structure_mapping'] = retrieveAtomicStructureMapping(matched_pdb_structure, matched_pdb_structure['translation_to_structure_mapping'])
                
                # add the matched and mapped structure to the PDB structure mappings
                PDBStructureMappings.append(matched_pdb_structure)
            except (AtomicSequenceIDMappingFailedException) as e:
                _log.error(e)
         
    # Retrieve the codons from the cDNA translation 
    translationCodons = []
    for i in range(0, len(gene_protein_translation_sequence)): translationCodons.append(coding_sequence[i * 3 : i * 3 + 3])
    
    # Finsh the cDNA and Genome mapping
    for i in range(1, cDNA_pos+1):
        genome_position = GenomeMapping['cDNA'][i]['Genome']
        n = int((i-1) / 3)
        
        # add codon to the mapping
        GenomeMapping['cDNA'][i]['translation_codon'] = translationCodons[n]
        GenomeMapping['Genome'][genome_position]['translation_codon'] = GenomeMapping['cDNA'][i]['translation_codon']
        
        # add codon allele number to the mapping
        GenomeMapping['cDNA'][i]['translation_codon_allele_pos'] = ((i-1)%3)
        GenomeMapping['Genome'][genome_position]['translation_codon_allele_pos'] = GenomeMapping['cDNA'][i]['translation_codon_allele_pos']
        
        # Add residue from translation
        GenomeMapping['cDNA'][i]['translation_residue'] = gene_protein_translation_sequence[n]
        GenomeMapping['Genome'][genome_position]['translation_residue'] = GenomeMapping['cDNA'][i]['translation_residue']
        
        # Add information for uniprot
        GenomeMapping['cDNA'][i]['uniprot'], GenomeMapping['cDNA'][i]['uniprot_residue'] = map_single_residue(translation_to_uniprot_mapping, n)
        GenomeMapping['Genome'][genome_position]['uniprot'], GenomeMapping['Genome'][genome_position]['uniprot_residue'] = GenomeMapping['cDNA'][i]['uniprot'], GenomeMapping['cDNA'][i]['uniprot_residue']
        
        if has_structure:
            for matched_pdb_structure in PDBStructureMappings:
                # Add pdb seqres mapping
                GenomeMapping['cDNA'][i][matched_pdb_structure['sseqid']+'_seqres'], GenomeMapping['cDNA'][i][matched_pdb_structure['sseqid']+'_seqres_residue'] = map_single_residue(matched_pdb_structure['translation_to_seqres_mapping'], n)
                GenomeMapping['Genome'][genome_position][matched_pdb_structure['sseqid']+'_seqres'], GenomeMapping['Genome'][genome_position][matched_pdb_structure['sseqid']+'_seqres_residue'] = GenomeMapping['cDNA'][i][matched_pdb_structure['sseqid']+'_seqres'], GenomeMapping['cDNA'][i][matched_pdb_structure['sseqid']+'_seqres_residue']
                
                # Add pdb structure mapping
                GenomeMapping['cDNA'][i][matched_pdb_structure['sseqid']+'_structure'], GenomeMapping['cDNA'][i][matched_pdb_structure['sseqid']+'_structure_residue'] = map_single_residue(matched_pdb_structure['translation_to_structure_mapping'], n, matched_pdb_structure['measured_structure_mapping'])
                GenomeMapping['Genome'][genome_position][matched_pdb_structure['sseqid']+'_structure'], GenomeMapping['Genome'][genome_position][matched_pdb_structure['sseqid']+'_structure_residue'] = GenomeMapping['cDNA'][i][matched_pdb_structure['sseqid']+'_structure'], GenomeMapping['cDNA'][i][matched_pdb_structure['sseqid']+'_structure_residue']
    
    return GenomeMapping


def extract_pdb_from_gene_region(gene_mapping, gene_region):
    """Expects a gene_region, as created by 'extract_gene_region' with 
    key/values: {'chr':chromosome, 'regions':chromosome_ranges}
    Returns: 
    {'PDB_ID': 
        {'CHAIN_ID': 
            {UNIPROT_POS: 
                {'pos': 'PDB_STRUCTURE_POS', 
                'residue': 'PDB_STRUCTURE_RESIDUE'
                }
            },
            ...
        },
        ...
    },..
    """
    pdb_structures = dict()
    not_pdb_keys = ['translation_codon_allele_pos', 'uniprot_residue', 'cDNA', 'uniprot', 'translation_codon', 'translation_residue', 'allele']
    for chr_range in gene_region['regions']:
        for i in range(chr_range[0], chr_range[1]+1):
            chr_pos = gene_region['chr']+":"+str(i)
            for key in gene_mapping['GenomeMapping']['Genome'][chr_pos].keys():
                uniprot_pos = gene_mapping['GenomeMapping']['Genome'][chr_pos]['uniprot']
                # focus only on pdb structure entries
                if key not in not_pdb_keys:
                    key_tokenized = key.split('_')
                    pdb_id = key_tokenized[0]
                    chain_id = key_tokenized[1]
    
                    if pdb_id not in pdb_structures.keys():
                        pdb_structures[pdb_id] = dict()
    
                    if chain_id not in pdb_structures[pdb_id].keys():
                        pdb_structures[pdb_id][chain_id] = dict()
                        
                    if uniprot_pos not in pdb_structures[pdb_id][chain_id].keys():
                        pdb_structures[pdb_id][chain_id][uniprot_pos] = dict()
    
                    if 'residue' in key:
                        pdb_structures[pdb_id][chain_id][uniprot_pos]['residue']= gene_mapping['GenomeMapping']['Genome'][chr_pos][key]
                        # check if the residue is identical to the swissprot residue
                        if gene_mapping['GenomeMapping']['Genome'][chr_pos][key] == gene_mapping['GenomeMapping']['Genome'][chr_pos]['uniprot_residue']:
                            pdb_structures[pdb_id][chain_id][uniprot_pos]['identical_sprot_residue'] = True
                        else:
                            pdb_structures[pdb_id][chain_id][uniprot_pos]['identical_sprot_residue'] = False
                    else:
                        pdb_structures[pdb_id][chain_id][uniprot_pos]['pos']= gene_mapping['GenomeMapping']['Genome'][chr_pos][key]
                        
    return pdb_structures

def extract_gene_region(gene_mapping, region_start, region_stop):    
    cdna_positions = []
    chromosome_positions = []
    uniprot_positions = []
    chromosome = ""
    for mapping_key in sorted(gene_mapping['GenomeMapping']['cDNA'].keys(), key=lambda x: int(x)):
        mapping_element = gene_mapping['GenomeMapping']['cDNA'][mapping_key]
        
        if chromosome == "":
            chromosome = mapping_element['Genome'].split(':')[0]
        if mapping_element['uniprot'] != '-':
            if region_start <= mapping_element['uniprot'] < region_stop:
                cdna_positions.append(mapping_key)
                chromosome_positions.append(int(mapping_element['Genome'].split(':')[1]))
                uniprot_positions.append(mapping_element['uniprot'])
            
    # check if thet domains are fully mapped
    protein_region_length = len(gene_mapping['uniprot']['sequence'][region_start:region_stop])
    if(protein_region_length != len(np.unique(uniprot_positions))):
        raise RegioncDNALengthDoesNotEqualProteinLengthException("analysis of protein region could not be made due to: protein_region_length != len(uniprot_positions)")
        
    # convert the chromosome to ranges
    chromosome_ranges = list(convertListOfIntegerToRanges(sorted(chromosome_positions)))
    
    return {'chr':chromosome, 'regions':chromosome_ranges, 'cdna_positions':cdna_positions, 'uniprot_positions':uniprot_positions, 'protein_region_length':protein_region_length}

