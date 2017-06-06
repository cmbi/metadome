'''
Created on Jun 30, 2016

Implements InterProScan methods for use throughout the project

@author: laurensvdwiel
'''
import tempfile
from metadom_api.default_settings import INTERPROSCAN_EXECUTABLE
import logging
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
