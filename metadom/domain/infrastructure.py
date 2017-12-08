from metadom.database import db
from metadom.domain.models.protein import Protein
from metadom.domain.models.chromosome import Chromosome

def add_gene_mapping_to_database(gene_mapping):
    for transcription_id in gene_mapping["genes"].keys():
        with db.session.no_autoflush:
            # retrieve the gene_translation
            gene_translation = gene_mapping["genes"][transcription_id]

            if transcription_id in gene_mapping["proteins"].keys():
                # test if this protein already exists in the database
                matching_protein = db.session.query(Protein).filter_by(uniprot_ac = gene_mapping["proteins"][transcription_id].uniprot_ac).first()
                protein_already_present = True
                if matching_protein is None:
                    # Protein is already present in the dataase, remove it from the to-be-added proteins
                    matching_protein = gene_mapping["proteins"].pop(transcription_id)
                    protein_already_present = False
                    
                # add relationships to mapping from gene translation and protein
                for chromosome_position in gene_mapping["mappings"][transcription_id].keys():
                    gene_translation.mappings.append(gene_mapping["mappings"][transcription_id][chromosome_position])
                    matching_protein.mappings.append(gene_mapping["mappings"][transcription_id][chromosome_position])
        
                # merge all chromosomes that are already present in the database
                for each in db.session.query(Chromosome).filter((Chromosome.chromosome == gene_mapping["chromosome_positions"][transcription_id][chromosome_position].chromosome) &\
                                                     (Chromosome.position.in_(gene_mapping["chromosome_positions"][transcription_id].keys()))).all():
                    gene_mapping["chromosome_positions"][transcription_id].pop(each.position)
                    each.mappings.append(gene_mapping["mappings"][transcription_id][each.position])
                
                # add each chromosomal postion not yet present in the database
                for each in gene_mapping["chromosome_positions"][transcription_id].keys():
                    gene_mapping["chromosome_positions"][transcription_id][each].mappings.append(gene_mapping["mappings"][transcription_id][each])
                
                # add the gene translation to the database
                db.session.add(gene_translation)
                
                # add the protein to the database
                if not protein_already_present:
                    db.session.add(matching_protein)
                
                # add all other objects to the database
                db.session.add_all(gene_mapping["mappings"][transcription_id].values())
                
                # add the remaining chromosome positions
                db.session.add_all(gene_mapping["chromosome_positions"][transcription_id].values())                        
            else:
                # add the gene translation to the database
                db.session.add(gene_translation)
        # Commit the changes of this mapping
        db.session.commit()
            
    # Close this session, thus all items are cleared and memory usage is kept at a minimum
    db.session.close()