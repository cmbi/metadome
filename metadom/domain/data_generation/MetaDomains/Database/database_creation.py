import pandas as pd
from sklearn.externals.joblib.parallel import Parallel, delayed
import sqlite3
import json
from BGVM.MetaDomains.Construction.meta_domain_creation import create_annotated_meta_domain
from BGVM.Tools.ParallelHelper import CalculateNumberOfActiveThreads
from BGVM.Tools.CustomLogger import initLogging
from BGVM.Domains.HomologuesDomains import load_homologue_domain_dataset
from dev_settings import LOGGER_NAME, GENE2PROTEIN_META_DOMAIN_DB,\
    GENE2PROTEIN_ANNOTATED_HOMOLOGUE_DOMAINS_DATASET
from meta_domain_database_settings import DATABASE_META_DOMAINS_TABLE,\
    DATABASE_META_DOMAINS_ID, DATABASE_META_DOMAINS_TABLE_COLUMNS,\
    DATABASE_META_DOMAINS_JSON_VALUE, FILTER_ON_MISSENSE_ONLY,\
    FILTER_ON_MINIMAL_EXAC_FREQUENCY
import logging
import time
from BGVM.Tools.DataIO import CustomJSONEncoder

def create_meta_domain_database(data, reconstruct_database=False, use_parallel=True, batch_size=50):    
    logging.getLogger(LOGGER_NAME).info("Started creating the 'meta'-domains dataset")
    start_time = time.clock()
    
    # If needed, reconstruct the database 
    if reconstruct_database:
        createNewMetaDomainDatabase()
    
    # Retrieve the domain ids
    domain_ids = pd.unique(data.external_database_id)
    
    # Create batches
    batches = [domain_ids[i:i+batch_size] for i in range(0, len(domain_ids), batch_size)]
    n_batches = len(batches)
    n_domains = len(domain_ids)
    
    # Annotate the genes in batches
    logging.getLogger(LOGGER_NAME).info("Starting the construction of '"+str(n_domains)+"' meta domains over '"+str(n_batches)+"' batches")
    for batch_counter, batch in enumerate(batches):
        logging.getLogger(LOGGER_NAME).info("Starting batch '"+str(batch_counter+1)+"' out of '"+str(n_batches)+"', with '"+str(len(batch))+"' domains")
    
        dataset_batch = []
        if use_parallel:
            dataset_batch = Parallel(n_jobs=CalculateNumberOfActiveThreads(batch_size))(delayed(create_annotated_meta_domain)(domain_id, data, FILTER_ON_MINIMAL_EXAC_FREQUENCY, FILTER_ON_MISSENSE_ONLY) for domain_id in batch)
        else:
            dataset_batch = [create_annotated_meta_domain(domain_id, data, FILTER_ON_MINIMAL_EXAC_FREQUENCY, FILTER_ON_MISSENSE_ONLY) for domain_id in batch]
        
        
        # remove empty meta_domains
        dataset_batch = [g for g in dataset_batch if not(g is None)]
        
        # add to database
        insert_batch_of_meta_domains(dataset_batch)
        
        # add number of succesful genes to the counter
        logging.getLogger(LOGGER_NAME).info("Finished batch '"+str(batch_counter+1)+"' out of '"+str(n_batches)+"'")    

    time_step = time.clock()
    logging.getLogger(LOGGER_NAME).info("Finished creating '"+str(n_domains)+"' 'meta'-domains over '"+str(n_batches)+"' batches in "+str(time_step-start_time)+" seconds")

def createNewMetaDomainDatabase():
    logging.getLogger(LOGGER_NAME).info("Started dropping (if exists) and creating the database for Meta domains at '"+GENE2PROTEIN_META_DOMAIN_DB+"'")
    
    conn = sqlite3.connect(GENE2PROTEIN_META_DOMAIN_DB)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS "+DATABASE_META_DOMAINS_TABLE)
    cur.execute("CREATE TABLE IF NOT EXISTS "+DATABASE_META_DOMAINS_TABLE+" ("+DATABASE_META_DOMAINS_TABLE_COLUMNS+");")
    cur.execute("CREATE INDEX IF NOT EXISTS gencode_gene_id_index ON "+DATABASE_META_DOMAINS_TABLE+" ("+DATABASE_META_DOMAINS_ID+");")
    conn.commit()
    conn.close()
    
    logging.getLogger(LOGGER_NAME).info("Finshed dropping and creating the database for Meta domains at '"+GENE2PROTEIN_META_DOMAIN_DB+"'")

def insert_batch_of_meta_domains(dataset_batch):
    conn = sqlite3.connect(GENE2PROTEIN_META_DOMAIN_DB)
    cur = conn.cursor()
     
    InsertQueries = [(domain["domain_id"], json.dumps(domain, cls=CustomJSONEncoder)) for domain in dataset_batch]
    cur.executemany("INSERT INTO "+DATABASE_META_DOMAINS_TABLE+" ("+DATABASE_META_DOMAINS_ID+", "+DATABASE_META_DOMAINS_JSON_VALUE+") VALUES (?,?)", InsertQueries)
     
    conn.commit()
    conn.close()
