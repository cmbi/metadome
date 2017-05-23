import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

Base = declarative_base()


class Chromosome(Base):
    """
    Table: chromosomes
    
    Fields
    id                        identifier
    chromosome                chromosome '1'-'22', 'X' or 'Y'
    position                  position in the chromosome
    
    Relationships
    mappings                  one to many relationship with Mapping
    """
    
    # Table configuration
    __tablename__ = 'chromosomes'
    
    # Fields
    id = Column(Integer, primary_key=True)
    chromosome = Column(String(2))
    position = Column(Integer)
    
    # Relationships
    mappings = relationship('Mapping', back_populates="chromosome")
    
    def __repr__(self):
        return "<Chromosome(chromosome='%s', position='%s')>" % (
                            self.chromosome, self.position)
    
class Mapping(Base):
    """
    Table: mapping
    
    Fields
    id                        identifier
    allele                    'A', 'T', 'C', 'G'
    codon                     all triplet combinations of the alleles 
    codon_allele_position     0, 1, 2, or None
    amino_acid_residue        one of the 20 amino acids, * or None
    cDNA_position             the position in the cDNA
    uniprot_position          the position in the protein
    pfam_consensus_position   position in the aligned Pfam domain or None
    
    Relationships
    """
    # Table configuration
    __tablename__ = 'mapping'
    
    # Fields
    id = Column(Integer, primary_key=True)
    allele = Column(String(1))
    codon = Column(String(3))
    codon_allele_position = Column(Integer)
    amino_acid_residue = Column(String(1))
    cDNA_position = Column(Integer)
    uniprot_position = Column(Integer)
    pfam_consensus_position = Column(Integer)
    chromosome_id = Column(Integer, ForeignKey('chromosomes.id'))
    
    # Relationships
    chromosome = relationship('Chromosome', back_populates="mappings")
    
#     "relationships": {
#         "meta_domains": {
#             "data": [
#                 { "type": "mapping", "id": 2 }
#             ]
#         },
#         "genes": {
#             "data": [
#                 { "type": "gene", "id": "ENST00000320580.4" }
#             ]
#         },
#         "proteins": {
#             "data": [
#                 { "type": "protein", "id": "Q6VY07" }
#             ]
#         },
#         "pfams": {
#             "data": [
#                 { "type": "pfam", "id": 1 }
#             ]
#         }
#     }
    
    def __repr__(self):
        return "<Mapping(allele='%s', codon='%s', codon_allele_position='%s', amino_acid_residue='%s', cDNA_position='%s', uniprot_position='%s', pfam_consensus_position='%s')>" % (
                            self.allele, self.codon, self.codon_allele_position, self.amino_acid_residue, self.cDNA_position, self.uniprot_position, self.pfam_consensus_position)
    
    
class Pfam(Base):
    """
    Table: pfam
    
    Fields
    id                        identifier
    pfam_id                   Pfam identifier code 'PF#####'
    name                      Name of the Pfam domain
    interpro_id               Interpro identifier  
    uniprot_ac                uniprot accession code
    uniprot_start             0 <= uniprot_start < uniprot_stop
    uniprot_stop              uniprot_stop <= uniprot_end
    """
    
    __tablename__ = 'pfam'
    
    id = Column(Integer, primary_key=True)
    pfam_id = Column(String(12))
    name = Column(String)
    interpro_id = Column(String(12))  
    uniprot_ac = Column(String(12), ForeignKey('protein.uniprot_ac'))
    uniprot_start = Column(Integer)
    uniprot_stop = Column(Integer)
    
    def __repr__(self):
        return "<Pfam(pfam_id='%s', name='%s', interpro_id='%s', uniprot_ac='%s', uniprot_start='%s', uniprot_stop='%s')>" % (
                            self.pfam_id, self.name, self.interpro_id, self.uniprot_ac, self.uniprot_start, self.uniprot_stop)

class Protein(Base):
    """
    Table: protein
    
    Fields
    id                        identifier
    uniprot_ac                uniprot accession code
    uniprot_name              uniprot name
    source                    'swissprot' or 'uniprot'
    """
    
    class ProteinSource(enum.Enum):
        uniprot = 'uniprot'
        swissprot = 'swissprot'
    
    
    __tablename__ = 'protein'
    
    id = Column(Integer, primary_key=True)
    uniprot_ac = Column(String(12), unique=True)
    uniprot_name = Column(String(20))
    source = Column(Enum(ProteinSource))

    def __repr__(self):
        return "<Protein(uniprot_ac='%s', uniprot_name='%s', source='%s')>" % (
                            self.uniprot_ac, self.uniprot_name, self.source)

class Gene(Base):
    """
    Table: gene
    
    Fields
    id                        identifier
    strand                    '+' or '-'
    gene_name                 Conventional (HAVANA) name of the gene
    gencode_transcription_id  e.g. ENST####...
    gencode_translation_name  e.g. BRCA1-###
    gencode_gene_id           e.g. ENSG####...
    havana_gene_id            e.g. OTTHUMG#####....
    havana_translation_id     e.g. OTTHUMT#####....
    """
    
    class Strand(enum.Enum):
        plus = '+'
        minus = '-'
        
    __tablename__ = 'gene'
    
    id = Column(Integer, primary_key=True)
    strand = Column(Enum(Strand))
    gene_name = Column(String(50))
    gencode_transcription_id = Column(String(50), unique=True)
    gencode_translation_name = Column(String(50), unique=True)
    gencode_gene_id = Column(String(50), unique=True)
    havana_gene_id = Column(String(50), unique=True)
    havana_translation_id = Column(String(50), unique=True)
    
    def __repr__(self):
        return "<Gene(strand='%s', gene_name='%s', gencode_transcription_id='%s', gencode_translation_name='%s', gencode_gene_id='%s', havana_gene_id='%s', havana_translation_id='%s')>" % (
                            self.strand, self.gene_name, self.gencode_transcription_id, self.gencode_translation_name, self.gencode_gene_id, self.havana_gene_id, self.havana_translation_id)
        

_locus = [
        {
            "locus":{
                "chromosome":"11",
                "position":65837965,
            },
            "locus_information": [
                    {
                        "information":{
                            "chromosome":"11",
                            "chromosome_position":65837965,
                            'cDNA_position':8,
                            'uniprot_position' : 2,
                            'strand': '+',
                            'allele': 'A',
                            'codon': 'GAA',
                            'codon_allele_position': 1,
                            'amino_acid_residue': 'E',
                            'gene_name' : 'PACS1',
                            'gencode_transcription_id' : 'ENST00000320580.4',
                            'gencode_translation_name' : 'PACS1-001',
                            'gencode_gene_id' : 'ENSG00000175115.7',
                            'havana_gene_id' : 'OTTHUMG00000166889.3',
                            'havana_translation_id' : 'OTTHUMT00000391690.2',
                            'uniprot_ac' : 'Q6VY07',
                            'uniprot_name' : 'PACS1_HUMAN',
                            'pfam_domain_consensus_position' : None,
                            'pfam_domain_name' : None,
                            'pfam_domain_id' : None,
                            'interpro_id' : None,
                            'uniprot_domain_start_pos' : None,
                            'uniprot_domain_end_pos' : None,
                        },
                        "meta_information":[],
                    },
                ],
        },
         {
            "locus":{
                "chromosome":"11",
                "position":66000499,
            },
            "locus_information": [
                    {
                        "information":{
                            "chromosome":"11",
                            "chromosome_position":66000499,
                            'cDNA_position':1800,
                            'uniprot_position' : 599,
                            'strand': '+',
                            'allele': 'G',
                            'codon': 'CAG',
                            'codon_allele_position': 2,
                            'amino_acid_residue': 'Q',
                            'gene_name' : 'PACS1',
                            'gencode_transcription_id' : 'ENST00000320580.4',
                            'gencode_translation_name' : 'PACS1-001',
                            'gencode_gene_id' : 'ENSG00000175115.7',
                            'havana_gene_id' : 'OTTHUMG00000166889.3',
                            'havana_translation_id' : 'OTTHUMT00000391690.2',
                            'uniprot_ac' : 'Q6VY07',
                            'uniprot_name' : 'PACS1_HUMAN',
                            'pfam_domain_consensus_position' : 123,
                            'pfam_domain_name' : 'PACS-1 cytosolic sorting protein',
                            'pfam_domain_id' : 'PF10254',
                            'interpro_id' : 'IPR019381',
                            'uniprot_domain_start_pos' : 548,
                            'uniprot_domain_end_pos' : 958,
                        },
                        "meta_information":[
                            "PACS2"
                        ]
                    },
                ],
        },
    ]

if __name__ == '__main__':
    from sqlalchemy import create_engine
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    
    chrompos = Chromosome(chromosome='11', position=66000499)
    