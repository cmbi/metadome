from metadom.infrastructure import database
from metadom.domain.models.mapping import Mapping
from metadom.domain.models.chromosome import Chromosome
from metadom.domain.models.gene import Gene
from metadom.domain.models.protein import Protein
from metadom.domain.models.pfam import Pfam

## Simulate the database
from sqlalchemy import create_engine
from sqlalchemy import and_
engine = create_engine('sqlite:///:memory:', echo=True)
database.Base.metadata.create_all(engine)

## Save the schema of the database
from sqlalchemy_schemadisplay import create_schema_graph

# create the pydot graph object by autoloading all tables via a bound metadata object
graph = create_schema_graph(metadata=database.Base.metadata,
   show_datatypes=True, # The image would get nasty big if we'd show the datatypes
   show_indexes=True, # ditto for indexes
   rankdir='LR', # From left to right (instead of top to bottom)
   concentrate=False # Don't try to join the relation lines together
)
graph.write_png('dbschema.png') # write out the file

## test with real data
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

_mapping_pacs1_1 = Mapping(allele='G',
                         codon='CAG',
                         codon_allele_position=2,
                         amino_acid_residue='Q',
                         cDNA_position=1800,
                         uniprot_position=599,
                         pfam_consensus_position=52,)
_mapping_pacs1_2 = Mapping(allele='A',
                         codon='GAA',
                         codon_allele_position=1,
                         amino_acid_residue='E',
                         cDNA_position=8,
                         uniprot_position=2,)
_mapping_pacs2_1 = Mapping(allele='C',
                         codon='CAG',
                         codon_allele_position=0,
                         amino_acid_residue='Q',
                         cDNA_position=1585,
                         uniprot_position=528,
                         pfam_consensus_position=52,)

_chrompos_pacs1_1 = Chromosome(chromosome='11', position=66000499)
_chrompos_pacs1_2 = Chromosome(chromosome='11', position=65837965)
_chrompos_pacs2_1 = Chromosome(chromosome='14', position=105849210)

_gene_pacs1 = Gene(strand=Gene.Strand.plus, gene_name='PACS1',
            gencode_transcription_id='ENST00000320580.4', 
            gencode_translation_name='PACS1-001', 
            gencode_gene_id='ENSG00000175115.7',
            havana_gene_id='OTTHUMG00000166889.3',
            havana_translation_id='OTTHUMT00000391690.2',)
_gene_pacs2 = Gene(strand=Gene.Strand.plus, gene_name='PACS2',
            gencode_transcription_id='ENST00000458164.2', 
            gencode_translation_name='PACS2-001', 
            gencode_gene_id='ENSG00000179364.9',
            havana_gene_id='OTTHUMG00000170450.1',
            havana_translation_id='OTTHUMT00000409210.1',)
                               
_protein_pacs1 = Protein(uniprot_ac='Q6VY07', 
                         uniprot_name='PACS1_HUMAN', 
                         source=Protein.ProteinSource.swissprot,)
_protein_pacs2 = Protein(uniprot_ac='Q86VP3-2', 
                         uniprot_name='PACS2_HUMAN', 
                         source=Protein.ProteinSource.swissprot,)

_pfam_domain_pacs1_1 = Pfam(pfam_id='PF10254', 
                          name='PACS-1 cytosolic sorting protein', 
                          interpro_id='IPR019381',
                          uniprot_ac='Q6VY07',
                          uniprot_start=548,
                          uniprot_stop=958,)
_pfam_domain_pacs2_1 = Pfam(pfam_id='PF10254', 
                          name='PACS-1 cytosolic sorting protein', 
                          interpro_id='IPR019381',
                          uniprot_ac='Q86VP3-2',
                          uniprot_start=477,
                          uniprot_stop=900,)

_chrompos_pacs1_1.mappings.append(_mapping_pacs1_1)
_chrompos_pacs1_2.mappings.append(_mapping_pacs1_2)
_chrompos_pacs2_1.mappings.append(_mapping_pacs2_1)
_gene_pacs1.mappings.append(_mapping_pacs1_1)
_gene_pacs1.mappings.append(_mapping_pacs1_2)
_gene_pacs2.mappings.append(_mapping_pacs2_1)
_protein_pacs1.mappings.append(_mapping_pacs1_1)
_protein_pacs1.mappings.append(_mapping_pacs1_2)
_protein_pacs2.mappings.append(_mapping_pacs2_1)
_pfam_domain_pacs1_1.mappings.append(_mapping_pacs1_1)
_pfam_domain_pacs2_1.mappings.append(_mapping_pacs2_1)
_protein_pacs1.pfam_domains.append(_pfam_domain_pacs1_1)
_protein_pacs2.pfam_domains.append(_pfam_domain_pacs2_1)

session.add(_mapping_pacs1_1)
session.add(_mapping_pacs1_2)
session.add(_mapping_pacs2_1)
session.add(_chrompos_pacs1_1)
session.add(_chrompos_pacs1_2)
session.add(_chrompos_pacs2_1)
session.add(_gene_pacs1)
session.add(_gene_pacs2)
session.add(_protein_pacs1)
session.add(_protein_pacs2)
session.add(_pfam_domain_pacs1_1)
session.add(_pfam_domain_pacs2_1)
session.commit()

# Test query
for x in session.query(Mapping).join(Pfam).filter(and_(Mapping.pfam_consensus_position==52, Pfam.pfam_id == 'PF10254')):
    for y in session.query(Chromosome).filter(Chromosome.id == x.chromosome_id):
        print(y,x)
