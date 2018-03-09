import logging

from metadom.database import db
from metadom.domain.models.mapping import Mapping
from metadom.domain.models.chromosome import Chromosome
from metadom.domain.models.gene import Gene
from metadom.domain.models.protein import Protein
from metadom.domain.models.interpro import Interpro
from metadom.domain.models.pfam_domain_alignment import PfamDomainAlignment

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

_log = logging.getLogger(__name__)

class GeneRepository:
    
    @staticmethod
    def retrieve_all_transcript_ids(gene_name):
        return [transcript_id for transcript_id in db.session.query(Gene.gencode_transcription_id).filter(Gene.gene_name == gene_name).all()]
    
    @staticmethod
    def retrieve_gene(transcription_id):
        try:
            gene = db.session.query(Gene).filter(Gene.gencode_transcription_id == transcription_id).one()
            return gene
        except MultipleResultsFound as e:
            _log.error("GeneRepository.retrieve_gene(transcription_id): Multiple results found while expecting uniqueness for transcription_id '"+str(transcription_id)+"'. "+e)
        except NoResultFound as  e:
            _log.error("GeneRepository.retrieve_gene(transcription_id): Expected results but found none for transcription_id '"+str(transcription_id)+"'. "+e)
        return None
    
class InterproRepository:
    
    @staticmethod
    def get_pfam_domains_for_transcript(transcript_id):
        # TODO: retrieve the domains for this transcript
        pass
    
class PfamDomainAlignmentRepository:
    
    @staticmethod
    def get_msa_alignment(entry_id):
        # TODO: remove when testing is done
        _log.info("got entry:" +str(entry_id))
        
        domain_alignments = []        
#         domain_occurrences = Interpro.query.filter(Interpro.ext_db_id.like(entry_id)).all()
#         alignment_positions = [x.alignment_position for x in PfamDomainAlignment.query.join(Interpro).filter((Interpro.id == PfamDomainAlignment.domain_id) & (Interpro.ext_db_id.like(entry_id))).distinct(PfamDomainAlignment.alignment_position)]
#         for domain_entry in domain_occurrences:
#             protein = domain_entry.get_protein()
#             alignment_entries = {x.alignment_position:x.get_aligned_residue() for x in PfamDomainAlignment.query.filter(domain_entry.id == PfamDomainAlignment.domain_id).order_by( PfamDomainAlignment.alignment_position).all()}
#             
#             aligned_sequence = ""
#             for alignment_pos in alignment_positions:
#                 if alignment_pos in alignment_entries.keys():
#                     aligned_sequence += alignment_entries[alignment_pos]
#                 else:
#                     aligned_sequence += '.'
#             
#             alignment_row = {"uniprot_start":domain_entry.uniprot_stop, 
#                              "uniprot_stop":domain_entry.uniprot_stop,
#                              "uniprot_name":protein.uniprot_name,
#                              "uniprot_ac":protein.uniprot_ac,
#                              "aligned_sequence":aligned_sequence}
#             
#             domain_alignments.append(alignment_row)
        
        return domain_alignments

class MappingRepository:
    
    @staticmethod
    def get_mappings_and_chromosomes_from_gene(_gene):
        return {x.Mapping.cDNA_position:x for x in Mapping.query.join(Chromosome).add_columns(Chromosome.chromosome, Chromosome.position).filter(Mapping.gene_id == _gene.id).all()}

    @staticmethod
    def get_mappings_position(entry_id, position):
        # TODO: remove when testing is done
        _log.info("got entry:" +str(entry_id)+" and position: "+str(position))
         
        # Default mapping
        mapping = {}
         
        # TODO: create handling of specific type of queries
        # TODO: make use of services
        
        # This is a pfam with position query
        for x in Mapping.query.join(PfamDomainAlignment).join(Interpro).filter(
            (Interpro.ext_db_id.like(entry_id)) &
            (PfamDomainAlignment.domain_consensus_position == position)):
            for y in db.session.query(Chromosome).filter(Chromosome.id ==
                                                        x.chromosome_id):
                chr_key = str(y.chromosome)+":"+str(y.position)
                if chr_key in mapping:
                    _log.error('Dublicate chromosome entry')
                else:
                    mapping[chr_key] = str(x)
          
        _log.info('got mapping: '+str(mapping))
        return mapping
