'''
Function to help interpret fasta files

@author: laurens
'''

def unwrap_fasta_alignment(alignment):
    """Unwraps a .fasta alignment by removing the end of line
    characters and formatting the fasta sequences as 
    [identifier_1, sequence_1, ..., identifier_N, sequence_N]"""
    new = []
    for i in alignment:
        if i.startswith('>'):
            new.append(i)
            new.append("")
        else:
            new[-1] += i
    return new