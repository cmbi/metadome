import logging

from metadom.domain.data_generation.mapping.Protein2ProteinMapping import createMappingOfAASequenceToAASequence,\
    map_single_residue
import numpy as np

from metadom.domain.models.mapping import Mapping
from metadom.domain.models.chromosome import Chromosome
from metadom.domain.models.gene import Gene
from metadom.domain.models.protein import Protein
from metadom.domain.models.pfam import Pfam
from metadom.database import db

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

def createMappingOfGeneTranscriptionToTranslationToProtein(gene_transcription, matching_coding_translation, uniprot):
    with db.session.no_autoflush as _session:
        # Retrieve the amino acid sequence according to the translation
        gene_protein_translation_sequence = matching_coding_translation['sequence']
        # Retrieve the canonical uniprot sequence
        canonical_protein_sequence = uniprot["sequence"]
        # nucleotide sequence containing of the CDS
        coding_sequence = gene_transcription['coding-sequence']
        # CDS for nucleotide positions
        cds =  gene_transcription['CDS_annotation']
        
        # Retrieve gene translation from database...
        gene_translation = Gene.query.filter_by(gencode_transcription_id = matching_coding_translation['transcription-id']).first()
        
        # Retrieve protein entry from database...
        matching_protein = Protein.query.filter_by(uniprot_ac = uniprot['uniprot_ac']).first()
            
        # check if there are multiple chromosomal positions
        chr_in_cds = list(set([cd.seqid for cd in cds]))
        if len(chr_in_cds) > 1:
            _log.warning('Found multiple chromosomes in coding sequence: '+str(chr_in_cds)+', using only '+str(chr_in_cds[0])+', this may indicate pseudoautosomal genes')
        
        # ensure we have the stop codon at the end of the translation sequence
        gene_protein_translation_sequence+='*'
        
        # test if mapping is already present in database
        if gene_translation is None:
            _log.error("Gene transcription "+matching_coding_translation['transcription-id']+" was not present in database. No Mapping was generated")
            return
        elif matching_protein is None:
            _log.error("Protein "+uniprot['uniprot_ac']+" was not present in database. No Mapping was generated")
            return
        elif gene_translation.get_aa_sequence()==gene_protein_translation_sequence and\
            gene_translation.get_cDNA_sequence()==coding_sequence and\
            matching_protein.get_aa_sequence()==(canonical_protein_sequence+"*"):
            _log.info("Gene transcription "+str(gene_translation.gencode_transcription_id)+" was already succesfully mapped to protein "+str(matching_protein.uniprot_ac)+". No Mapping was generated")
            return 
        
        # align cDNA sequence with uniprot canonical sequence
        translation_to_uniprot_mapping  = createMappingOfAASequenceToAASequence(gene_protein_translation_sequence, canonical_protein_sequence)
        
        # Retrieve the codons from the cDNA translation 
        translationCodons = []
        for i in range(0, len(gene_protein_translation_sequence)): translationCodons.append(coding_sequence[i * 3 : i * 3 + 3])
        
        # Create mapping between Gene and cDNA
        cDNA_pos = 0
        currentChr = ''
        to_be_added_chrom_pos = []
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
                # create mapping object for this position
                allele = coding_sequence[cDNA_pos]
                
                # increment cDNA position
                cDNA_pos = cDNA_pos+1
                aa_pos = int((cDNA_pos-1) / 3)
                
                # add chromosome entry in database if it does not already exists
                chrom_pos = Chromosome.query.filter_by(chromosome=str(cd.seqid), position=i).first()
                if chrom_pos is None:
                    chrom_pos = Chromosome(chromosome=str(cd.seqid), position=i)
                    to_be_added_chrom_pos.append(chrom_pos) 
                
                # add codon to the mapping
                codon = translationCodons[aa_pos]                
                # add codon allele number to the mapping
                codon_allele_position = ((cDNA_pos-1)%3)
                # Add residue from translation
                amino_acid_residue = gene_protein_translation_sequence[aa_pos]
                # Add information for uniprot
                if amino_acid_residue == '*':
                    uniprot_residue = '*'
                    uniprot_position = None
                    aa_pos = None
                else:
                    uniprot_position, uniprot_residue = map_single_residue(translation_to_uniprot_mapping, aa_pos)
                
                # create the mapping
                mapping = Mapping(
                    allele = allele,
                    cDNA_position = cDNA_pos,
                    codon = codon,
                    codon_allele_position = codon_allele_position,
                    amino_acid_residue = amino_acid_residue,
                    amino_acid_position = aa_pos,
                    uniprot_position = uniprot_position,
                    uniprot_residue = uniprot_residue
                    )
                
                chrom_pos.mappings.append(mapping)
                gene_translation.mappings.append(mapping)
                matching_protein.mappings.append(mapping)
    
                # add mapping to the database
                _session.add(mapping)
            to_be_added_chrom_pos = []
    
        # add all other objects to the database
        for x in to_be_added_chrom_pos:
            _session.add(x)
        
        _session.commit()


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

