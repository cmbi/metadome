'''
Created on Aug 3, 2016

@author: laurens
'''
import sqlite3
import json
import urllib.request
from dev_settings import GENE2PROTEIN_META_DOMAIN_DB
from meta_domain_database_settings import DATABASE_META_DOMAINS_ID,\
    DATABASE_META_DOMAINS_TABLE, DATABASE_META_DOMAINS_JSON_VALUE

def retrieve_all_meta_domains():
    """Retrieves all meta domain entries as:
    domain_id | meta_domain"""
    # connect to the database and retrieve the cursor
    conn = sqlite3.connect(GENE2PROTEIN_META_DOMAIN_DB, check_same_thread=False)
    cur = conn.cursor()
     
    # Construct query
    query = "SELECT "+DATABASE_META_DOMAINS_ID+", "+DATABASE_META_DOMAINS_JSON_VALUE+" FROM "+DATABASE_META_DOMAINS_TABLE
     
    # execute query
    for row in cur.execute(query):
        yield interpretRowAsMetaDomain(row)
    conn.close()

def retrieve_single_meta_domain(domain_id):
    """Retrieves a single meta domain entry based on the domain_id and returns the entry  as:
    domain_id | meta_domain"""
    # connect to the database and retrieve the cursor
    conn = sqlite3.connect(GENE2PROTEIN_META_DOMAIN_DB)
    cur = conn.cursor()
     
    # Constrct query
    t = (domain_id,)
    query =  "SELECT "+DATABASE_META_DOMAINS_ID+", "+DATABASE_META_DOMAINS_JSON_VALUE+" FROM "+DATABASE_META_DOMAINS_TABLE+" WHERE "+DATABASE_META_DOMAINS_ID+"=?"
     
    # execute query
    meta_domain = None
    
    for row in cur.execute(query, t):
        if not(meta_domain is None):
            raise Exception("gene name is not unique for"+str(meta_domain))
        meta_domain = interpretRowAsMetaDomain(row)
    conn.close()

    return meta_domain
   
def retrieve_all_meta_domain_ids():
    """Retrieves all domain_id's in the meta domain database"""
    # connect to the database and retrieve the cursor
    conn = sqlite3.connect(GENE2PROTEIN_META_DOMAIN_DB, check_same_thread=False)
    cur = conn.cursor()
     
    # Construct query
    query = "SELECT "+DATABASE_META_DOMAINS_ID+" FROM "+DATABASE_META_DOMAINS_TABLE
     
    # execute query
    for row in cur.execute(query):
        yield urllib.request.unquote(row[0])
    conn.close()

def interpretRowAsMetaDomain(row):
    meta_domain = {
        "domain_id": urllib.request.unquote(row[0]),
        "meta_domain": json.loads(row[1]),
    }
    
    return meta_domain