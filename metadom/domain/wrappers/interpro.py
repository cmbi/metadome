import logging
from metadom.default_settings import INTERPROSCAN_EXECUTABLE, INTERPRO_PRO2IPR_DB
import sqlite3
import urllib.request
import tempfile
import subprocess
import os

_log = logging.getLogger(__name__)

def run_interproscan_query(query_id, sequence):
    """Runs the interproscan service for a given sequence
    The TSV format presents the match data in columns as follows:

    1. Protein Accession (e.g. P51587)
    2. Sequence MD5 digest (e.g. 14086411a2cdf1c4cba63020e1622579)
    3. Sequence Length (e.g. 3418)
    4. Analysis (e.g. Pfam / PRINTS / Gene3D)
    5. Signature Accession (e.g. PF09103 / G3DSA:2.40.50.140)
    6. Signature Description (e.g. BRCA2 repeat profile)
    7. Start location
    8. Stop location
    9. Score - is the e-value of the match reported by member database method (e.g. 3.1E-52)
    10. Status - is the status of the match (T: true)
    11. Date - is the date of the run
    12. (InterPro annotations - accession (e.g. IPR002093) - optional column; only displayed if -iprlookup option is switched on)
    13. (InterPro annotations - description (e.g. BRCA2 repeat) - optional column; only displayed if -iprlookup option is switched on)
    14. (GO annotations (e.g. GO:0005515) - optional column; only displayed if --goterms option is switched on)
    15. (Pathways annotations (e.g. REACT_71) - optional column; only displayed if --pathways option is switched on)"""
    # create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".fasta", delete=False) as tmp_file:
        tmp_file.write(('\n'.join(['>'+str(query_id), sequence])).encode(encoding='utf_8', errors='strict'))
    out_interproscan = tmp_file.name + '.iprscan'
    
    args = [INTERPROSCAN_EXECUTABLE, "--input", tmp_file.name, "--outfile", out_interproscan, "--iprlookup", "--formats", "TSV"]
    
    try:
        subprocess.call(args)
    except subprocess.CalledProcessError as e:
        _log.error("{}".format(e.output))

    if os.path.exists(out_interproscan):
        with open(out_interproscan) as a:
            output = a.read().splitlines()
        logging.debug(output)
        if output:
            logging.debug('output True')
        os.remove(out_interproscan)
    else:
        output = []
    os.remove(tmp_file.name)
    
    # return interproscan results
    return output

def retrieve_interpro_entries(uniprot_data):
    output =  [interpro_entry for interpro_entry in retrieve_interpro_entries_from_db(uniprot_data['uniprot_ac'])]
    if len(output) == 0:
        _log.info("Found no matching InterPro hits on uniprot ac '"+uniprot_data['uniprot_ac']+"', attempting to query interproscan")
    
        # no results found, attempt a query to interproscan
        interproscan_output = run_interproscan_query(uniprot_data['uniprot_ac'], uniprot_data['sequence'])
        output = [interpro_entry for interpro_entry in interpret_output_of_interproscan_query(interproscan_output)]
        
        if len(output) == 0:
            _log.info("Found no matching InterProScan hits on uniprot ac '"+uniprot_data['uniprot_ac']+"'")
    
    return output

def interpret_output_of_interproscan_query(output):
    for output_entry in output:
        output_entry = output_entry.split('\t')
        if len(output_entry) == 11:
            interpro_id = None
        else:
            interpro_id = urllib.request.unquote(output_entry[11])
        
        interpro_entry = {
            "uniprot_ac": urllib.request.unquote(output_entry[0]),
            "interpro_id": interpro_id,
            "region_name": None if output_entry[5] == "NULL" else urllib.request.unquote(output_entry[5]),
            "ext_db_id": None if output_entry[4] == "NULL" else urllib.request.unquote(output_entry[4]),
            "start_pos": None if output_entry[6] == "NULL" else int(output_entry[6]),
            "end_pos": None if output_entry[7] == "NULL" else int(output_entry[7]),
        }
        yield interpro_entry

def retrieve_interpro_entries_from_db(uniprot_id):
    """Retrieves interpro entries based on the uniprot id and returns the entries as:
    UniprotID | InterprotID | Region_name | ext_db_id | start_pos | end_pos"""
    # connect to the database and retrieve the cursor
    conn = sqlite3.connect(INTERPRO_PRO2IPR_DB)
    cur = conn.cursor()
    
    # Constrct query
    t = (uniprot_id,)
    query = 'SELECT uniprot_ac, interpro_id, region_name, ext_db_id, start_pos, end_pos FROM interpro2prot WHERE uniprot_ac=?'
    
    # execute query
    for row in cur.execute(query, t):
        #format entry as UniprotID | InterprotID | Region_name | ext_db_id | start_pos | end_pos
        interpro_entry = {
            "uniprot_ac": urllib.request.unquote(row[0]),
            "interpro_id": urllib.request.unquote(row[1]),
            "region_name": None if row[2] == "NULL" else urllib.request.unquote(row[2]),
            "ext_db_id": None if row[3] == "NULL" else urllib.request.unquote(row[3]),
            "start_pos": None if row[4] == "NULL" else int(row[4]),
            "end_pos": None if row[5] == "NULL" else int(row[5]),
        }
        # re
        #Alternatively, you can emit the dictionary here, if you need mutability:
        yield interpro_entry
    conn.close()