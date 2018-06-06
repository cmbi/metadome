# import unittest
# import os
# from metadome.default_settings import DATA_DIR, BLASTP_EXECUTABLE,\
#     CLUSTALW_EXECUTABLE, GENCODE_HG_ANNOTATION_FILE_GTF,\
#     GENCODE_HG_ANNOTATION_FILE_GFF3, GENCODE_HG_TRANSCRIPTION_FILE,\
#     GENCODE_HG_TRANSLATION_FILE, GENCODE_SWISSPROT_FILE, GENCODE_BASIC_FILE,\
#     GENE_MAPPING_DIR, GENE_STRUCTURE_ANNOTATION_DIR,\
#     GENE_STRUCTURE_CLUSTER_RESULTS_DIR, PDB_DIR, PDB_STRUCTURE_DIR,\
#     PDB_SEQRES_FASTA, HOMMOD_DIR, HOMMOD_STRUCTURE_DIR,\
#     HOMMOD_FASTA, LOGGER_NAME, MINIMAL_BLASTPE_VALUE,\
#     MINIMAL_TRANSLATION_TO_HOMMOL_STRUCTURE_PIDENT_VALUE,\
#     MINIMAL_TRANSLATION_TO_HOMMOL_STRUCTURE_COVERAGE_VARIATION,\
#     MINIMAL_TRANSLATION_TO_PDB_STRUCTURE_PIDENT_VALUE,\
#     MINIMAL_XRAY_STRUCTURE_RESOLUTION
# 
# class Test_default_settings(unittest.TestCase):
#     def test_directory_and_file_existence(self):
#         # local data directory
#         self.assertTrue(os.path.isdir(DATA_DIR))
#         
#         # local executables
#         self.assertTrue(os.path.isfile(BLASTP_EXECUTABLE))
#         self.assertTrue(os.path.isfile(CLUSTALW_EXECUTABLE))
#         
#         # Genome specific files
#         self.assertTrue(os.path.isfile(GENCODE_HG_ANNOTATION_FILE_GTF))
#         self.assertTrue(os.path.isfile(GENCODE_HG_ANNOTATION_FILE_GFF3))
#         self.assertTrue(os.path.isfile(GENCODE_HG_TRANSCRIPTION_FILE))
#         self.assertTrue(os.path.isfile(GENCODE_HG_TRANSLATION_FILE))
#         self.assertTrue(os.path.isfile(GENCODE_SWISSPROT_FILE))
#         self.assertTrue(os.path.isfile(GENCODE_BASIC_FILE))
#         
#         # Gene mapping specific files
#         self.assertTrue(os.path.isdir(GENE_MAPPING_DIR))
#         self.assertTrue(os.path.isdir(GENE_STRUCTURE_ANNOTATION_DIR))
#         self.assertTrue(os.path.isdir(GENE_STRUCTURE_CLUSTER_RESULTS_DIR))
#         
#         # PDB specific files
#         self.assertTrue(os.path.isdir(PDB_DIR))
#         self.assertTrue(os.path.isdir(PDB_STRUCTURE_DIR))
#         self.assertTrue(os.path.isfile(PDB_SEQRES_FASTA))
#         
#         # Homology modelling
#         self.assertTrue(os.path.isdir(HOMMOD_DIR))
#         self.assertTrue(os.path.isdir(HOMMOD_STRUCTURE_DIR))
#         self.assertTrue(os.path.isfile(HOMMOD_FASTA))
#         
#     def test_valid_configuration(self):
#         # custom logging
#         self.assertTrue(type(LOGGER_NAME) is str)
#         self.assertTrue(len(LOGGER_NAME)>0)
#         
#         # Configuration
#         self.assertTrue(type(MINIMAL_BLASTPE_VALUE) is float)
#         self.assertTrue(MINIMAL_BLASTPE_VALUE>=0.0)
#         self.assertTrue(MINIMAL_BLASTPE_VALUE<=1.0)
#         
#         self.assertTrue(type(MINIMAL_TRANSLATION_TO_HOMMOL_STRUCTURE_PIDENT_VALUE) is float)
#         self.assertTrue(MINIMAL_TRANSLATION_TO_HOMMOL_STRUCTURE_PIDENT_VALUE>=0.0)
#         self.assertTrue(MINIMAL_TRANSLATION_TO_HOMMOL_STRUCTURE_PIDENT_VALUE<=1.0)
#         
#         self.assertTrue(type(MINIMAL_TRANSLATION_TO_HOMMOL_STRUCTURE_COVERAGE_VARIATION) is float)
#         self.assertTrue(MINIMAL_TRANSLATION_TO_HOMMOL_STRUCTURE_COVERAGE_VARIATION>=0.0)
#         self.assertTrue(MINIMAL_TRANSLATION_TO_HOMMOL_STRUCTURE_COVERAGE_VARIATION<=1.0)
#         
#         self.assertTrue(type(MINIMAL_TRANSLATION_TO_PDB_STRUCTURE_PIDENT_VALUE) is float)
#         self.assertTrue(MINIMAL_TRANSLATION_TO_PDB_STRUCTURE_PIDENT_VALUE>=0.0)
#         self.assertTrue(MINIMAL_TRANSLATION_TO_PDB_STRUCTURE_PIDENT_VALUE<=1.0)
# 
#         self.assertTrue(type(MINIMAL_XRAY_STRUCTURE_RESOLUTION) is float)
#         self.assertTrue(MINIMAL_XRAY_STRUCTURE_RESOLUTION>=0.0)
#         self.assertTrue(MINIMAL_XRAY_STRUCTURE_RESOLUTION<=100.0) # according to Gert the worst measured structure in existence is around 86 Angstrom
# 
# if __name__ == "__main__":
#     #import sys;sys.argv = ['', 'Test.testName']
#     unittest.main()