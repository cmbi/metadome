import logging

from metadome.database import db
from metadome.domain.models.mapping import Mapping
from metadome.domain.models.gene import Gene
from metadome.domain.models.protein import Protein
from metadome.domain.models.interpro import Interpro

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql.functions import func
from metadome.default_settings import GENE_NAMES_FILE
from sqlalchemy.sql.expression import and_, distinct

_log = logging.getLogger(__name__)

class MalformedAARegionException(Exception):
    pass


class GeneRepository:
    
    @staticmethod
    def retrieve_all_gene_names_from_file():
        """Retrieves all gene names present in the static file"""
        gene_names = []
        try:
            with open(GENE_NAMES_FILE, 'r') as gene_names_file:
                gene_names = gene_names_file.read().splitlines()
        except OSError:
            return []
        return gene_names
    
    @staticmethod
    def retrieve_all_gene_names_from_db():
        """Retrieves all gene names present in the database"""
        return [gene_name for gene_name in db.session.query(Gene.gene_name).distinct(Gene.gene_name).all()]
    
    @staticmethod
    def retrieve_all_transcript_ids(gene_name):
        """Retrieves all transcript ids for a gene name"""
        return [transcript for transcript in db.session.query(Gene).filter(func.lower(Gene.gene_name) == gene_name.lower()).all()]
    
    @staticmethod
    def retrieve_gene(transcription_id):
        """Retrieves the gene object for a given transcript id"""
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
    def get_all_Pfam_identifiers_suitable_for_metadomains():
        """Retrieves all pfam identifiers that occur at least two times in the database"""
        for domain_entry in Interpro.query.with_entities(Interpro.ext_db_id, func.count(Interpro.id)).filter(Interpro.ext_db_id.like('PF%')).group_by(Interpro.ext_db_id).having(func.count(Interpro.id)>2).distinct(Interpro.ext_db_id):
            yield domain_entry.ext_db_id
    
    
    @staticmethod
    def get_all_Pfam_identifiers():
        """Retrieves all pfam identifiers present in the database"""
        for domain_entry in Interpro.query.filter(Interpro.ext_db_id.like('PF%')).distinct(Interpro.ext_db_id):
            yield domain_entry.ext_db_id
    
    @staticmethod
    def get_domains_for_ext_domain_id(ext_domain_id):
        """Retrieves all interpro entries of the corresponding ext_db_id"""
        return [interpro_domain for interpro_domain in db.session.query(Interpro).filter(Interpro.ext_db_id == ext_domain_id).all()]
    
    @staticmethod
    def get_domains_for_protein(protein_id):
        """Retrieves all interpro entries for a given protein_id"""
        return [interpro_domain for interpro_domain in db.session.query(Interpro).filter(Interpro.protein_id == protein_id).all()]
    
class ProteinRepository:
    
    @staticmethod
    def retrieve_protein_ac_for_multiple_protein_ids(_protein_ids):
        """Retrieves all uniprot accession codes for multiple Protein objects as {protein_id: uniprot_ac}"""
        _protein_ac_per_protein_id = {}
        for protein in db.session.query(Protein).filter(Protein.id.in_(_protein_ids)).all():
            _protein_ac_per_protein_id[protein.id] = protein.uniprot_ac
        return _protein_ac_per_protein_id
    
    @staticmethod
    def retrieve_protein_id_for_multiple_protein_acs(_protein_acs):
        """Retrieves all protein ids for multiple Protein objects as {protein_ac: uniprot_id}"""
        _protein_id_per_protein_ac = {}
        for protein in db.session.query(Protein).filter(Protein.uniprot_ac.in_(_protein_acs)).all():
            _protein_id_per_protein_ac[protein.uniprot_ac] = protein.id
        return _protein_id_per_protein_ac
    
    
    @staticmethod
    def retrieve_protein(protein_id):
        """Retrieves the protein object for a given protein id"""
        try:
            protein = db.session.query(Protein).filter(Protein.id == protein_id).one()
            return protein
        except MultipleResultsFound as e:
            _log.error("ProteinRepository.retrieve_protein(protein_id): Multiple results found while expecting uniqueness for protein_id '"+str(protein_id)+"'. "+e)
        except NoResultFound as  e:
            _log.error("ProteinRepository.retrieve_protein(protein_id): Expected results but found none for protein_id '"+str(protein_id)+"'. "+e)
        return None

class MappingRepository:
    
    @staticmethod
    def get_mappings_for_multiple_protein_ids(_protein_ids):
        """Retrieves all mappings for a multiple Protein objects as {protein_id: [ Mapping ]}"""
        _mappings_per_protein = {}
        for mapping in db.session.query(Mapping).filter(Mapping.protein_id.in_(_protein_ids)).all():
            if not mapping.protein_id in _mappings_per_protein:
                _mappings_per_protein[mapping.protein_id] = []
                
            _mappings_per_protein[mapping.protein_id].append(mapping)
        return _mappings_per_protein
    
    @staticmethod
    def get_mappings_for_protein(_protein):
        """Retrieves all mappings for a Protein object"""
        return [x for x in db.session.query(Mapping).filter(Mapping.protein_id == _protein.id).all()]
    
    @staticmethod
    def get_mappings_for_gene(_gene):
        """Retrieves all mappings for a Gene object"""
        return [x for x in db.session.query(Mapping).filter(Mapping.gene_id == _gene.id).all()]
    
class SequenceRepository:
    
    @staticmethod
    def get_aa_sequence(mappings, skip_asterix_at_end=False):
        """For a list of mappings, returns the amino acid sequence based on the uniprot positions
        If an asterix is expected at the end (e.g. a stop codon) there is the posibility to skip that"""
        _aa_sequence = ""
        mappings = {x.uniprot_position:x.uniprot_residue for x in mappings}
        for key in sorted(mappings, key=lambda x: (x is None, x)):
            # type check this is all the same protein and gene
            
            # type check if there are any gaps
            
            if skip_asterix_at_end and key is None:
                continue
            _aa_sequence+= mappings[key]
        return _aa_sequence
    
    @staticmethod
    def get_aa_region(sequence, region_start, region_stop):
        """For a given sequence, returns the sub-sequence
        based on the region_start and region stop"""
        # type check region start and region stop
        if region_start < 0 or region_stop > len(sequence) or region_stop < region_start:
            raise MalformedAARegionException("For sequence of length '"+str(len(sequence))+
                                              "': received a faulty  attempted to build a gene region where_region_stop < _region_start")        

        
        # Return the sub sequence
        return sequence[region_start-1:region_stop]
    
    @staticmethod
    def get_cDNA_sequence(mappings):
        """For a list of mappings, returns the cDNA sequence based on the cDNA positions"""
        _cDNA_sequence = ""
        mappings = {x.cDNA_position:x.base_pair for x in mappings}
        for key in sorted(mappings.keys()):
            _cDNA_sequence+= mappings[key]
        return _cDNA_sequence