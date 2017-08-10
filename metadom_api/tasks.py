#!flask/bin/python
from flask import Flask, jsonify, abort, make_response
# import metadom_api.application
# 
# from flask import current_app as flask_app

app = Flask(__name__)

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

@app.route('/metadom/api/chr/<int:chr>/<int:position>', methods=['GET'])
def get_chr_pos(chr,position):
    locus = [x for x in _locus if x['locus']['chromosome'] == chr and x['locus']['position']==position]
    if len(locus) == 0:
        abort(404)
    return jsonify({'locus': locus[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    
    app.run(debug=True)
    