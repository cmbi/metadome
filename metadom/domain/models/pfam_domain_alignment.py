from metadom.database import db
from metadom.domain.models.mapping import Mapping
from metadom.domain.models.protein import Protein

class PfamDomainAlignment(db.Model):
    """
    Table: pfam_domain_alignment
    Contains a aligned positions of uniprot residues to 
    Pfam domain occurrences in uniprot sequences
    
    Fields
    id                        identifier
    domain_consensus_position The consensus position of the pfam domain
    domain_consensus_residue  The consensus residue of the pfam domain
    mapping_id                Foreign key
    protein_id                Foreign key
    
    Relationships
    many to one               mappings
    many to one               protein
    """
    # Table configuration
    __tablename__ = 'pfam_domain_alignments'
    
    # Fields
    id = db.Column(db.Integer, primary_key=True)
    alignment_position = db.Column(db.Integer, nullable=False)
    domain_consensus_position = db.Column(db.Integer)
    domain_consensus_residue = db.Column(db.String(1))
    mapping_id = db.Column(db.Integer, db.ForeignKey('mappings.id'), nullable=False)
    domain_id = db.Column(db.Integer, db.ForeignKey('interpro_domains.id'), nullable=False)
    
    # Relationships
    mappings = db.relationship('Mapping', back_populates="pfam_domain_alignment")
    domain = db.relationship('Interpro', back_populates="pfam_domain_alignments")
    
    # Constraints
    __table_args__ = (db.UniqueConstraint('domain_id', 'mapping_id', name='_unique_protein_domain_position'),
                     )
        
    def get_aligned_residue(self):
        aligned_residue = Mapping.query.filter_by(id = self.mapping_id).first().uniprot_residue
        
        # double check if this is and insertion or an aligned residue
        if self.domain_consensus_position is None and self.domain_consensus_residue == '-':
            return aligned_residue.lower()
        else:
            return aligned_residue
    
    def get_protein(self):
        return Protein.query.join(Mapping).filter((Mapping.id == self.mapping_id)).first()

    def get_gene(self):
        return Gene.query.join(Mapping).filter((Mapping.id == self.mapping_id)).first()
      
    def get_domain_occurence(self):
        return Interpro.query.filter(id = domain_id).first()
    
    def __repr__(self):
        return "<PfamDomainAlignment(domain_id='%s', alignment_position='%s', mapping_id='%s')>" % (
                            self.domain_id, self.alignment_position, self.mapping_id)