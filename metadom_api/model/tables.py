import enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum

Base = declarative_base()


class Chromosome(Base):
    """
    Table: chromosomes
    
    Fields
    id                        identifier
    chromosome                chromosome '1'-'22', 'X' or 'Y'
    position                  position in the chromosome
    """
    
    __tablename__ = 'chromosomes'
    
    id = Column(Integer, primary_key=True)
    chromosome = Column(String(2))
    position = Column(Integer)
    
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
    """
    
    __tablename__ = 'mapping'
    
    id = Column(Integer, primary_key=True)
    allele = Column(String(1))
    codon = Column(String(3))
    codon_allele_position = Column(Integer)
    amino_acid_residue = Column(String(1))
    cDNA_position = Column(Integer)
    uniprot_position = Column(Integer)
    pfam_consensus_position = Column(Integer)
    
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
    uniprot_ac = Column(String(12))
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
    gencode_transcription_id = Column(String(50))
    gencode_translation_name = Column(String(50))
    gencode_gene_id = Column(String(50))
    havana_gene_id = Column(String(50))
    havana_translation_id = Column(String(50))
    
    def __repr__(self):
        return "<Gene(strand='%s', gene_name='%s', gencode_transcription_id='%s', gencode_translation_name='%s', gencode_gene_id='%s', havana_gene_id='%s', havana_translation_id='%s')>" % (
                            self.strand, self.gene_name, self.gencode_transcription_id, self.gencode_translation_name, self.gencode_gene_id, self.havana_gene_id, self.havana_translation_id)