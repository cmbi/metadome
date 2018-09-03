from metadome.domain.repositories import GeneRepository, RepositoryException
from metadome.domain.models.entities.gene_region import GeneRegion
from metadome.domain.models.entities.single_nucleotide_variant import SingleNucleotideVariant
from metadome.domain.models.entities.meta_domain import MetaDomain,\
    UnsupportedMetaDomainIdentifier
from metadome.domain.services.computation.gene_region_computations import compute_tolerance_landscape
from metadome.domain.services.annotation.gene_region_annotators import annotateTranscriptWithClinvarData
from metadome.domain.services.annotation.annotation import annotateSNVs
from metadome.domain.error import RecoverableError
import numpy as np

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

@celery_app.task(bind=True,
                 autoretry_for=(RecoverableError,),
                 retry_kwargs={'max_retries': 50})
def mock_response(self):
    _log.info('Mocking PTPN11...')
         
    from metadome.presentation.api.routes_mock import mockup_tol_and_metadom, mock_ptpn11
    return mock_ptpn11()


@celery_app.task(bind=True,
                 autoretry_for=(RecoverableError,),
                 retry_kwargs={'max_retries': 50})
def initialize_metadomain(self, domain_id):
    return MetaDomain.initializeFromDomainID(domain_id)


@celery_app.task(bind=True,
                 autoretry_for=(RecoverableError,),
                 retry_kwargs={'max_retries': 50})
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
 
@celery_app.task(bind=True,
                 autoretry_for=(RecoverableError,),
                 retry_kwargs={'max_retries': 50})
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
                        temp_meta_domain = MetaDomain.initializeFromDomainID(domain.ext_db_id)
                        
                        # Ensure there are enough instances to actually perform the metadomain trick
                        if temp_meta_domain.n_instances < 2:
                            pfam_domain["metadomain"] = False
                            meta_domains[pfam_domain['ID']] = None
                        else:
                            pfam_domain["metadomain"] = True
                            meta_domains[pfam_domain['ID']] = temp_meta_domain
                            pfam_domain['meta_domain_alignment_depth'] = temp_meta_domain.get_max_alignment_depth()
                        
                    else:
                        pfam_domain["metadomain"] = not(meta_domains[pfam_domain['ID']] is None)
                except UnsupportedMetaDomainIdentifier as e:
                    _log.error(str(e))
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
                protein_pos = _mappings_per_chromosome[chrom_pos]['amino_acid_position']
                 
                if not 'ClinVar' in region_positional_annotation[protein_pos].keys():
                    region_positional_annotation[protein_pos]['ClinVar'] = []
                 
                codon = gene_region.retrieve_codon_for_protein_position(protein_pos)
                 
                # create new entry for this variant
                variant_entry = SingleNucleotideVariant.initializeFromVariant(_codon=codon, _chr_position=chrom_pos, _alt_nucleotide=variant['ALT'], _variant_source='ClinVar').toDict()

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
                        consensus_positions = meta_domains[domain['ID']].get_consensus_positions_for_uniprot_position(uniprot_ac=gene_region.uniprot_ac, uniprot_position=db_position)
                        
                        if domain["metadomain"] and len(consensus_positions)>0:
                            d['domains'][domain['ID']] = create_meta_domain_entry(gene_region, meta_domains[domain['ID']], consensus_positions, db_position)
                            
        result = {"transcript_id":transcript_id, "protein_ac":gene_region.uniprot_ac, "gene_name":gene_region.gene_name, "positional_annotation":region_positional_annotation, "domains":Pfam_domains}
    else:
        result = {'error': 'No gene region could be build for transcript '+str(transcript_id)}
     
    return result

def create_meta_domain_entry(gene_region, metadomain, consensus_positions, protein_pos):
    metadom_entry = {}
    # update the consensus positions to abide the users' expectation (start at 1, not zero)
    metadom_entry['consensus_pos'] = [int(x) for x in np.array(consensus_positions)+1]
    metadom_entry['normal_missense_variant_count'] = 0
    metadom_entry['normal_variant_count'] = 0
    metadom_entry['pathogenic_missense_variant_count'] = 0
    metadom_entry['pathogenic_variant_count'] = 0
    
    for consensus_position in consensus_positions:
        # Retrieve the meta codons for this position
        meta_snvs = metadomain.get_annotated_SNVs_for_consensus_position(consensus_position)
        current_codon = gene_region.retrieve_codon_for_protein_position(protein_pos)
        # iterate over meta_codons and add to metadom_entry
        for meta_snv_repr in meta_snvs.keys():
            if not current_codon.unique_str_representation() in meta_snv_repr:
                # unique variant at homologous position, can just take the first from the list
                meta_snv = meta_snvs[meta_snv_repr][0]
            
                if meta_snv['variant_source'] == 'gnomAD':
                    # Update the variant counts
                    metadom_entry['normal_variant_count'] += 1
                    if meta_snv['variant_type'] == 'missense': metadom_entry['normal_missense_variant_count'] += 1
                elif meta_snv['variant_source'] == 'ClinVar':
                    # Update the variant counts
                    metadom_entry['pathogenic_variant_count'] += 1
                    if meta_snv['variant_type'] == 'missense': metadom_entry['pathogenic_missense_variant_count'] += 1
                     
    return metadom_entry
