'''
Created on Dec 22, 2015

@author: laurensvdwiel
'''

def match_sander_schneider_homology_alignment_treshold(alignment_length, identity):
    """Implements a check if the alignment meets the criteria posed in 'Sander, C., & Schneider,
    R. (1991). Database of homology-derived protein structures and the structural meaning of
    sequence alignment' Table 1."""
    if alignment_length >= 80:
        return identity >= 24.8
    if alignment_length >= 70:
        return identity >= 26.7
    if alignment_length >= 65:
        return identity >= 27.8
    if alignment_length >= 60:
        return identity >= 29.1
    if alignment_length >= 55:
        return identity >= 30.6
    if alignment_length >= 50:
        return identity >= 32.3
    if alignment_length >= 45:
        return identity >= 34.2
    if alignment_length >= 40:
        return identity >= 36.6
    if alignment_length >= 35:
        return identity >= 39.4
    if alignment_length >= 30:
        return identity >= 43.0
    if alignment_length >= 28:
        return identity >= 44.7
    if alignment_length >= 26:
        return identity >= 46.6
    if alignment_length >= 24:
        return identity >= 48.7
    if alignment_length >= 22:
        return identity >= 51.1
    if alignment_length >= 20:
        return identity >= 53.9
    if alignment_length >= 18:
        return identity >= 57.2
    if alignment_length >= 16:
        return identity >= 61.2
    if alignment_length >= 14:
        return identity >= 65.9
    if alignment_length >= 12:
        return identity >= 71.9
    if alignment_length >= 10:
        return identity >= 79.6
    return False