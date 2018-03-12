from metadom.database import db
from metadom.domain.models.protein import Protein
from metadom.domain.models.mapping import Mapping
from metadom.domain.models.pfam_domain_alignment import PfamDomainAlignment

def get_all_Pfam_identifiers():
    for domain_entry in Interpro.query.filter(Interpro.ext_db_id.like('PF%')).distinct(Interpro.ext_db_id):
        yield domain_entry.ext_db_id


class Interpro(db.Model):
    """
    Table: interpro_domains
    Contains the representation of Interpro domain occurrences
    in uniprot sequences
    
    Fields
    id                        identifier
    ext_db_id                 External domain database identifier code
    name                      Name of the Interpro domain
    domain_length               Length of the Interpro domain
    interpro_id               Interpro identifier
    uniprot_start             0 <= uniprot_start < uniprot_stop
    uniprot_stop              uniprot_stop <= uniprot_end
    protein_id                Foreign key
    
    Relationships
    many to one               protein
    one to many               pfam_domain_alignments
    """
    # Table configuration
    __tablename__ = 'interpro_domains'
    
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    ext_db_id = db.Column(db.String, nullable=False)
    region_name = db.Column(db.String)
    interpro_id = db.Column(db.String(12))
    uniprot_start = db.Column(db.Integer, nullable=False)
    uniprot_stop = db.Column(db.Integer, nullable=False)
    protein_id = db.Column(db.Integer, db.ForeignKey('proteins.id'), nullable=False)
    
    # Relationships
    protein = db.relationship("Protein", back_populates="interpro_domains")
    pfam_domain_alignments = db.relationship("PfamDomainAlignment", back_populates="domain")
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('protein_id', 'ext_db_id', 'uniprot_start', 'uniprot_stop', name='_unique_protein_region'),
                     )
    
    
#     def get_domain_alignment(self):
#         aligned_residues = Mapping.query.join(PfamDomainAlignment).filter(\
#             (Mapping.id == PfamDomainAlignment.mapping_id) &\
#             (PfamDomainAlignment.domain_id == self.id)).all()
#         
#         return aligned_residues
# #         mappings = {x.uniprot_position:x.uniprot_residue for x in Mapping.query.filter_by(protein_id = self.id).all()}
# #         for key in sorted(mappings):
# #             if region_start-1 <= key < region_stop:
# #                 
# #             if skip_asterix_at_end and key is None:
# #                 continue
# #             _aa_sequence+= mappings[key]
# #         return _aa_sequence
#     
#     def get_domain_alignment(self):
#         return PfamDomainAlignment.query.filter_by(domain_id = self.id).all()
#     
#     def get_pfam_alignment(self):
#         alignments = PfamDomainAlignment.query.filter_by(domain_id = self.id)
#         print(alignments)
# #         
# #         
# #         return PfamDomainAlignment.query.filter_by(domain_id = self.id)
    
    def get_protein(self):
        return Protein.query.filter_by(id = self.protein_id).first()
    
    def get_aa_sequence(self):
        return self.get_protein().get_aa_region(region_start=self.uniprot_start, region_stop=self.uniprot_stop)
    
    def __init__(self, _interpro_id, _ext_db_id, _region_name, _start_pos, _end_pos):
        self.interpro_id = _interpro_id
        self.ext_db_id = _ext_db_id
        self.region_name = _region_name
        self.uniprot_start = _start_pos
        self.uniprot_stop = _end_pos
    
    def __repr__(self):
        return "<Interpro(ext_db_id='%s', region_name='%s', interpro_id='%s', uniprot_start='%s', uniprot_stop='%s')>" % (
                            self.ext_db_id, self.region_name, self.interpro_id, self.uniprot_start, self.uniprot_stop)