from metadome.domain.repositories import GeneRepository, RepositoryException
from metadome.domain.models.entities.gene_region import GeneRegion
from metadome.domain.services.computation.gene_region_computations import compute_tolerance_landscape
from metadome.domain.models.entities.meta_domain import MetaDomain
from metadome.domain.services.annotation.gene_region_annotators import annotateTranscriptWithClinvarData,\
    annotateTranscriptWithGnomADData
from metadome.domain.services.annotation.annotation import annotateSNVs

from celery import current_app as celery_app
from flask import current_app as flask_app

import json
import os
import logging

_log = logging.getLogger(__name__)

def get_task(job_name):
    """
    Get the task for the given input_type and output_type combination.
    If the combination is not allowed, a ValueError is raised.
    """
    _log.debug(get_celery_worker_status())
     
    task = None
    if job_name == 'create':
        task = create_prebuild_visualization
    elif job_name == 'retrieve':
        task = retrieve_prebuild_visualization
    elif job_name == 'mock_it':
        task = mock_response
    else:
        raise ValueError("Unexpected input_type '{}'".format(job_name))
 
    _log.debug("Got task '{}'".format(task.__name__))
    return task

def get_celery_worker_status():
    """Used for retrieving celery status. Usefule for debug purposes"""
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d

@celery_app.task(bind=True)
def mock_response(self):
    _log.info('Mocking PTPN11...')
         
    from metadome.presentation.api.routes_mock import mockup_tol_and_metadom, mock_ptpn11
    return mock_ptpn11()

@celery_app.task(bind=True)
def retrieve_prebuild_visualization(self, transcript_id):
    _log.info("Getting prebuild visualization for '{}'".format(transcript_id))
 
    # Determine path to the file and check that it exists.
    visualization_path = flask_app.config['PRE_BUILD_VISUALIZATION_DIR'] + transcript_id + '/' + flask_app.config['PRE_BUILD_VISUALIZATION_FILE_NAME']
    if not os.path.exists(visualization_path):
        raise RuntimeError("File not found: '{}'".format(visualization_path))
 
    # Unzip the file and return the contents
    _log.info("Reading '{}'".format(visualization_path))
    with open(visualization_path) as f:
        visualization_content = json.load(f)
    return visualization_content
 
@celery_app.task(bind=True)
def create_prebuild_visualization(self, transcript_id):
    _log.info("Attempting to create visualization for '{}'".format(transcript_id))
    
    result = analyse_transcript(transcript_id)
    
    if 'error' in result.keys():
        _log.info("Something went wrong while trying to create visualization for '{}'".format(transcript_id))
        return result
    _log.info("Succeeded in creating visualization for '{}', saving as prebuild...".format(transcript_id))
    
    # Check if the directory already exists
    base_visualization_dir = flask_app.config['PRE_BUILD_VISUALIZATION_DIR']
    if not os.path.exists(base_visualization_dir):
        os.makedirs(base_visualization_dir)
        
    # Check if the directory for the gene already exists
    visualization_dir = base_visualization_dir + transcript_id + '/'
    if not os.path.exists(visualization_dir):
        os.makedirs(visualization_dir)
    
    # Determine path to the file and check that it exists.
    visualization_path = visualization_dir + flask_app.config['PRE_BUILD_VISUALIZATION_FILE_NAME']
             
    with open(visualization_path, 'w') as f:
        json.dump(result, f)
        
    return result

def analyse_transcript(transcript_id):
    # Retrieve the gene from the database
    try:
        gene = GeneRepository.retrieve_gene(transcript_id)
    except RepositoryException as e:
        return {'error': 'No gene region could be build for transcript {}, reason: {}'.format(transcript_id, e)}
    
    # build the gene region
    gene_region = GeneRegion(gene)
     
    if not gene_region is None:
        # generate the positional annotation for this gene by first computing the tolerance landscape
        region_positional_annotation = compute_tolerance_landscape(gene_region, flask_app.config['SLIDING_WINDOW_SIZE'], flask_app.config['ALLELE_FREQUENCY_CUTOFF'])
         
        # Annotate Pfam domains
        Pfam_domains = []
        meta_domains = {}
        for domain in gene_region.interpro_domains:
            if domain.ext_db_id.startswith('PF'):
                # we have a Pfam domain
                pfam_domain = {}
                pfam_domain["ID"] = domain.ext_db_id
                pfam_domain["Name"] = domain.region_name
                pfam_domain["start"] = domain.uniprot_start
                pfam_domain["stop"] = domain.uniprot_stop
                  
                try:
                    if not pfam_domain['ID'] in meta_domains.keys():
                        # construct a meta-domain if possible
                        temp_meta_domain = MetaDomain(domain.ext_db_id)
                        
                        # Ensure there are enough instances to actually perform the metadomain trick
                        if temp_meta_domain.n_instances < 2:
                            pfam_domain["metadomain"] = False
                            meta_domains[pfam_domain['ID']] = None
                        else:
                            pfam_domain["metadomain"] = True
                            meta_domains[pfam_domain['ID']] = temp_meta_domain
                        
                    else:
                        pfam_domain["metadomain"] = not(meta_domains[pfam_domain['ID']] is None)
                except:
                    # meta domain is not possible
                    meta_domains[pfam_domain['ID']] = None
                     
                # Add the domain to the domain list
                Pfam_domains.append(pfam_domain)
                 
        # Annotate the clinvar variants for the current gene
        ClinVar_annotation = annotateSNVs(annotateTranscriptWithClinvarData,
                                         mappings_per_chr_pos=gene_region.retrieve_mappings_per_chromosome(),
                                         strand=gene_region.strand, 
                                         chromosome=gene_region.chr,
                                         regions=gene_region.regions)
         
        # retrieve the mappings per chromosome position
        _mappings_per_chromosome = gene_region.retrieve_mappings_per_chromosome()
         
        for chrom_pos in ClinVar_annotation.keys():
            for variant in ClinVar_annotation[chrom_pos]:
                protein_pos = _mappings_per_chromosome[chrom_pos].uniprot_position
                 
                if not 'ClinVar' in region_positional_annotation[protein_pos].keys():
                    region_positional_annotation[protein_pos]['ClinVar'] = []
                 
                codon = gene_region.retrieve_codon_for_protein_position(protein_pos)
                 
                # create new entry for this variant
                variant_entry = {}
                # append variant information
                variant_entry['alt_codon'], variant_entry['alt_aa'], variant_entry['alt_aa_triplet'], variant_entry['type']  = codon.interpret_SNV_type(position=chrom_pos, var_nucleotide= variant['ALT'])
                variant_entry['pos'] = variant['POS']
                variant_entry['ref'] = variant['REF']
                variant_entry['alt'] = variant['ALT']
 
                # append ClinVar specific information
                variant_entry['clinvar_ID'] = variant['ID']
                 
                region_positional_annotation[protein_pos]['ClinVar'].append(variant_entry)
         
        # annotate the positions further
        for d in region_positional_annotation:
            # retrieve the position as is in the database
            db_position = d['protein_pos']
             
            # update the positions to abide the users' expectation (start at 1, not zero)
            d.update((k, v+1) for k, v in d.items() if k == "protein_pos")
             
            # add domain and meta domain information per position
            d['domains'] = {}
            for domain in Pfam_domains:
                if d['protein_pos'] >= domain["start"] and d['protein_pos'] <= domain["stop"]:
                    # add the domain id for this position
                    d['domains'][domain['ID']] = None 
                    if not meta_domains[domain['ID']] is None:
                        # retrieve the context for this protein
                        protein_to_consensus_positions = meta_domains[domain['ID']].consensus_pos_per_protein[gene_region.uniprot_ac]
                        if domain["metadomain"] and db_position in protein_to_consensus_positions.keys():
                            # update the consensus positions to abide the users' expectation (start at 1, not zero)
                            consensus_position = protein_to_consensus_positions[db_position]+1
                            d['domains'][domain['ID']] = create_meta_domain_entry(gene_region, meta_domains[domain['ID']], consensus_position, db_position)
                            
                            # compute alignment depth, added one for the current codon
                            current_alignment_depth = len(d['domains'][domain['ID']]['other_codons'])+1
                            
                            # update the max number of alignments for this domain
                            if not 'meta_domain_alignment_depth' in domain.keys():
                                domain['meta_domain_alignment_depth'] = 0
                            domain['meta_domain_alignment_depth'] = max(current_alignment_depth, domain['meta_domain_alignment_depth'])
                            
        result = {"transcript_id":transcript_id, "protein_ac":gene_region.uniprot_ac, "gene_name":gene_region.gene_name, "positional_annotation":region_positional_annotation, "domains":Pfam_domains}
    else:
        result = {'error': 'No gene region could be build for transcript '+str(transcript_id)}
     
    return result

def create_meta_domain_entry(gene_region, metadomain, consensus_position, protein_pos):
    metadom_entry = {}
    metadom_entry['consensus_pos'] = consensus_position
    metadom_entry['normal_missense_variant_count'] = 0
    metadom_entry['normal_synonymous_variant_count'] = 0
    metadom_entry['normal_nonsense_variant_count'] = 0
    metadom_entry['normal_variant_count'] = 0
    metadom_entry['pathogenic_missense_variant_count'] = 0
    metadom_entry['pathogenic_synonymous_variant_count'] = 0
    metadom_entry['pathogenic_nonsense_variant_count'] = 0    
    metadom_entry['pathogenic_variant_count'] = 0
    metadom_entry['other_codons'] = []
     
    # Retrieve the meta codons for this position
    meta_codons = metadomain.get_codons_aligned_to_consensus_position(metadom_entry['consensus_pos'])
    
    # iterate over meta_codons and add to metadom_entry
    for meta_codon in meta_codons:
        # Check if we are dealing with the gene and protein_pos of interest
        if not (gene_region.gene_id in meta_codon.codon_aggregate.keys() \
            and protein_pos == meta_codon.codon_aggregate[gene_region.gene_id].amino_acid_position):
            # first append the general information for this codon
            position_entry = {}
            position_entry['chr'] = meta_codon.chr
            position_entry['chr_positions'] = meta_codon.pretty_print_chr_region()
            position_entry['strand'] = meta_codon.strand.value
            position_entry['ref_aa'] = meta_codon.amino_acid_residue
            position_entry['ref_aa_triplet'] = meta_codon.three_letter_amino_acid_residue()
            position_entry['ref_codon'] = meta_codon.base_pair_representation
 
            # annotate missense from gnomad
            position_entry['normal_variants'] = []
            normal_variant_annotation = annotateSNVs(annotateTranscriptWithGnomADData,
                                     mappings_per_chr_pos=meta_codon.retrieve_mappings_per_chromosome(),
                                     strand=meta_codon.strand, 
                                     chromosome=meta_codon.chr,
                                     regions=meta_codon.regions)
             
            # process the annotation
            for chrom_pos in normal_variant_annotation.keys():
                for variant in normal_variant_annotation[chrom_pos]:
                    # create new entry for this variant
                    variant_entry = {}
                    # append variant information
                    variant_entry['alt_codon'], variant_entry['alt_aa'], variant_entry['alt_aa_triplet'], variant_entry['type']  = meta_codon.interpret_SNV_type(position=chrom_pos, var_nucleotide= variant['ALT'])
                    variant_entry['pos'] = variant['POS']
                    variant_entry['ref'] = variant['REF']
                    variant_entry['alt'] = variant['ALT']
 
                    # append gnomAD specific information
                    variant_entry['allele_number'] = variant['AN']
                    variant_entry['allele_count'] = variant['AC']
                     
                    # add to the position entry
                    position_entry['normal_variants'].append(variant_entry)
                     
                    # count the variants
                    if variant_entry['type'] == 'missense': metadom_entry['normal_missense_variant_count'] += 1
                    if variant_entry['type'] == 'synonymous': metadom_entry['normal_synonymous_variant_count'] += 1
                    if variant_entry['type'] == 'nonsense': metadom_entry['normal_nonsense_variant_count'] += 1
             
            # annotate pathogenic missense from clinvar
            position_entry['pathogenic_variants'] = []
            pathogenic_variant_annotation = annotateSNVs(annotateTranscriptWithClinvarData,
                                     mappings_per_chr_pos=meta_codon.retrieve_mappings_per_chromosome(),
                                     strand=meta_codon.strand, 
                                     chromosome=meta_codon.chr,
                                     regions=meta_codon.regions)
             
            # process the annotation
            for chrom_pos in pathogenic_variant_annotation.keys():
                for variant in pathogenic_variant_annotation[chrom_pos]:
                     
                    # create new entry for this variant
                    variant_entry = {}
                    # append variant information
                    variant_entry['alt_codon'], variant_entry['alt_aa'], variant_entry['alt_aa_triplet'], variant_entry['type']  = meta_codon.interpret_SNV_type(position=chrom_pos, var_nucleotide= variant['ALT'])
                    variant_entry['pos'] = variant['POS']
                    variant_entry['ref'] = variant['REF']
                    variant_entry['alt'] = variant['ALT']
 
                    # append ClinVar specific information
                    variant_entry['clinvar_ID'] = variant['ID']
                     
                    # add to the position entry
                    position_entry['pathogenic_variants'].append(variant_entry)
                     
                    # count the variants
                    if variant_entry['type'] == 'missense': metadom_entry['pathogenic_missense_variant_count'] += 1
                    if variant_entry['type'] == 'synonymous': metadom_entry['pathogenic_synonymous_variant_count'] += 1
                    if variant_entry['type'] == 'nonsense': metadom_entry['pathogenic_nonsense_variant_count'] += 1
             
            # add this codon to the metadome entry
            metadom_entry['other_codons'].append(position_entry)
             
            # Update the variant counts
            metadom_entry['normal_variant_count'] += len(position_entry['normal_variants'])
            metadom_entry['pathogenic_variant_count'] += len(position_entry['pathogenic_variants'])
     
    return metadom_entry