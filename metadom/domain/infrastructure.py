from metadom.database import db
from metadom.domain.models.protein import Protein
from metadom.domain.models.gene import Gene
from sqlalchemy.sql.expression import distinct
import logging

_log = logging.getLogger(__name__)

def filter_gene_names_present_in_database(gene_names_of_interest):
    _session = db.create_scoped_session()
    _log.info("Filtering gene names that are already present in the database ...")
    
    # Make sure the gene names are a set, so we can pop them
    gene_names_of_interest = set(gene_names_of_interest)

    # check which gene names are already present in the database
    n_gene_names = len(gene_names_of_interest)
    n_filtered_gene_names = 0
    for gene_name in _session.query(distinct(Gene.gene_name)).filter(Gene.gene_name.in_(gene_names_of_interest)).all():
        gene_names_of_interest.remove(gene_name[0])
        n_filtered_gene_names+=1
    
    _log.info("Filtered '"+str(n_filtered_gene_names)+"' out of '"+str(n_gene_names)+"' gene names that are already present in the database ...")
    
    # Close this session, thus all items are cleared and memory usage is kept at a minimum
    _session.remove()
    
    return list(gene_names_of_interest)

def add_gene_mapping_to_database(gene_mapping):
    _session = db.create_scoped_session()
    
    for transcription_id in gene_mapping["genes"].keys():
        with _session.no_autoflush:
            # retrieve the gene_translation
            gene_translation = gene_mapping["genes"][transcription_id]

            if transcription_id in gene_mapping["proteins"].keys():
                # test if this protein already exists in the database
                matching_protein = _session.query(Protein).filter_by(uniprot_ac = gene_mapping["proteins"][transcription_id].uniprot_ac).first()
                protein_already_present = True
                if matching_protein is None:
                    # Protein is already present in the dataase, remove it from the to-be-added proteins
                    matching_protein = gene_mapping["proteins"].pop(transcription_id)
                    protein_already_present = False
                    
                # add relationships to mapping from gene translation and protein
                for mapping in gene_mapping["mappings"][transcription_id]:
                    gene_translation.mappings.append(mapping)
                    matching_protein.mappings.append(mapping)
                    
                # add relationship from protein to gene transcript
                matching_protein.genes.append(gene_translation)
        
                # add the gene translation to the database
                _session.add(gene_translation)
                
                # add the protein to the database
                if not protein_already_present:
                    _session.add(matching_protein)
                
                # add all other objects to the database
                _session.add_all(gene_mapping["mappings"][transcription_id])       
            else:
                # add the gene translation to the database
                _session.add(gene_translation)
        # Commit the changes of this mapping
        _session.commit()
            
    # Close this session, thus all items are cleared and memory usage is kept at a minimum
    _session.remove()
