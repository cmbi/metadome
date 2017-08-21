from Bio.Seq import translate
import numpy as np

translate_code = {    'AAA', 'AAC', 'AAG', 'AAT',
                      'ACA', 'ACC', 'ACG', 'ACT',
                      'AGA', 'AGC', 'AGG', 'AGT',
                      'ATA', 'ATC', 'ATG', 'ATT',
                      'CAA', 'CAC', 'CAG', 'CAT',
                      'CCA', 'CCC', 'CCG', 'CCT',
                      'CGA', 'CGC', 'CGG', 'CGT',
                      'CTA', 'CTC', 'CTG', 'CTT',
                      'GAA', 'GAC', 'GAG', 'GAT',
                      'GCA', 'GCC', 'GCG', 'GCT',
                      'GGA', 'GGC', 'GGG', 'GGT', 
                      'GTA', 'GTC', 'GTG', 'GTT', 
                      'TAA', 'TAC', 'TAG', 'TAT', 
                      'TCA', 'TCC', 'TCG', 'TCT', 
                      'TGA', 'TGC', 'TGG', 'TGT', 
                      'TTA', 'TTC', 'TTG', 'TTT'
}

translate_residues = {'*', 'A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y',}

nucleotide_bases = {"A", "C", "T", "G"}

# Result
codon_background_rates = {
    'AAA': {'missense': 7, 'nonsense': 1, 'synonymous': 1},
    'AAC': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'AAG': {'missense': 7, 'nonsense': 1, 'synonymous': 1},
    'AAT': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'ACA': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'ACC': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'ACG': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'ACT': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'AGA': {'missense': 6, 'nonsense': 1, 'synonymous': 2},
    'AGC': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'AGG': {'missense': 7, 'nonsense': 0, 'synonymous': 2},
    'AGT': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'ATA': {'missense': 7, 'nonsense': 0, 'synonymous': 2},
    'ATC': {'missense': 7, 'nonsense': 0, 'synonymous': 2},
    'ATG': {'missense': 9, 'nonsense': 0, 'synonymous': 0},
    'ATT': {'missense': 7, 'nonsense': 0, 'synonymous': 2},
    'CAA': {'missense': 7, 'nonsense': 1, 'synonymous': 1},
    'CAC': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'CAG': {'missense': 7, 'nonsense': 1, 'synonymous': 1},
    'CAT': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'CCA': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'CCC': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'CCG': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'CCT': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'CGA': {'missense': 4, 'nonsense': 1, 'synonymous': 4},
    'CGC': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'CGG': {'missense': 5, 'nonsense': 0, 'synonymous': 4},
    'CGT': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'CTA': {'missense': 5, 'nonsense': 0, 'synonymous': 4},
    'CTC': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'CTG': {'missense': 5, 'nonsense': 0, 'synonymous': 4},
    'CTT': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GAA': {'missense': 7, 'nonsense': 1, 'synonymous': 1},
    'GAC': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'GAG': {'missense': 7, 'nonsense': 1, 'synonymous': 1},
    'GAT': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'GCA': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GCC': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GCG': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GCT': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GGA': {'missense': 5, 'nonsense': 1, 'synonymous': 3},
    'GGC': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GGG': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GGT': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GTA': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GTC': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GTG': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'GTT': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'TAA': {'missense': 0, 'nonsense': 7, 'synonymous': 2},
    'TAC': {'missense': 6, 'nonsense': 2, 'synonymous': 1},
    'TAG': {'missense': 0, 'nonsense': 8, 'synonymous': 1},
    'TAT': {'missense': 6, 'nonsense': 2, 'synonymous': 1},
    'TCA': {'missense': 4, 'nonsense': 2, 'synonymous': 3},
    'TCC': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'TCG': {'missense': 5, 'nonsense': 1, 'synonymous': 3},
    'TCT': {'missense': 6, 'nonsense': 0, 'synonymous': 3},
    'TGA': {'missense': 0, 'nonsense': 8, 'synonymous': 1},
    'TGC': {'missense': 7, 'nonsense': 1, 'synonymous': 1},
    'TGG': {'missense': 7, 'nonsense': 2, 'synonymous': 0},
    'TGT': {'missense': 7, 'nonsense': 1, 'synonymous': 1},
    'TTA': {'missense': 5, 'nonsense': 2, 'synonymous': 2},
    'TTC': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
    'TTG': {'missense': 6, 'nonsense': 1, 'synonymous': 2},
    'TTT': {'missense': 8, 'nonsense': 0, 'synonymous': 1},
}

# Result
codon_background_residues = {
    'AAA': {'K': 1, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 1, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 1, 'F': 0, 'I': 1, 'N': 2, '*': 1, 'E': 1, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'AAC': {'K': 2, 'Y': 1, 'H': 1, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 1, 'A': 0, 'T': 1, 'F': 0, 'I': 1, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'AAG': {'K': 1, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 1, 'V': 0, 'M': 1, 'R': 1, 'D': 0, 'A': 0, 'T': 1, 'F': 0, 'I': 0, 'N': 2, '*': 1, 'E': 1, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'AAT': {'K': 2, 'Y': 1, 'H': 1, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 1, 'A': 0, 'T': 1, 'F': 0, 'I': 1, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'ACA': {'K': 1, 'Y': 0, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 1, 'T': 3, 'F': 0, 'I': 1, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'ACC': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 0, 'A': 1, 'T': 3, 'F': 0, 'I': 1, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 2},
    'ACG': {'K': 1, 'Y': 0, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 0, 'M': 1, 'R': 1, 'D': 0, 'A': 1, 'T': 3, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'ACT': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 0, 'A': 1, 'T': 3, 'F': 0, 'I': 1, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 2},
    'AGA': {'K': 1, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 2, 'D': 0, 'A': 0, 'T': 1, 'F': 0, 'I': 1, 'N': 0, '*': 1, 'E': 0, 'W': 0, 'G': 1, 'C': 0, 'S': 2},
    'AGC': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 3, 'D': 0, 'A': 0, 'T': 1, 'F': 0, 'I': 1, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 1, 'C': 1, 'S': 1},
    'AGG': {'K': 1, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 1, 'R': 2, 'D': 0, 'A': 0, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 1, 'G': 1, 'C': 0, 'S': 2},
    'AGT': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 3, 'D': 0, 'A': 0, 'T': 1, 'F': 0, 'I': 1, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 1, 'C': 1, 'S': 1},
    'ATA': {'K': 1, 'Y': 0, 'H': 0, 'P': 0, 'L': 2, 'Q': 0, 'V': 1, 'M': 1, 'R': 1, 'D': 0, 'A': 0, 'T': 1, 'F': 0, 'I': 2, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'ATC': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 1, 'Q': 0, 'V': 1, 'M': 1, 'R': 0, 'D': 0, 'A': 0, 'T': 1, 'F': 1, 'I': 2, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'ATG': {'K': 1, 'Y': 0, 'H': 0, 'P': 0, 'L': 2, 'Q': 0, 'V': 1, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 1, 'F': 0, 'I': 3, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'ATT': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 1, 'Q': 0, 'V': 1, 'M': 1, 'R': 0, 'D': 0, 'A': 0, 'T': 1, 'F': 1, 'I': 2, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'CAA': {'K': 1, 'Y': 0, 'H': 2, 'P': 1, 'L': 1, 'Q': 1, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 1, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'CAC': {'K': 0, 'Y': 1, 'H': 1, 'P': 1, 'L': 1, 'Q': 2, 'V': 0, 'M': 0, 'R': 1, 'D': 1, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'CAG': {'K': 1, 'Y': 0, 'H': 2, 'P': 1, 'L': 1, 'Q': 1, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 1, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'CAT': {'K': 0, 'Y': 1, 'H': 1, 'P': 1, 'L': 1, 'Q': 2, 'V': 0, 'M': 0, 'R': 1, 'D': 1, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 1, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'CCA': {'K': 0, 'Y': 0, 'H': 0, 'P': 3, 'L': 1, 'Q': 1, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 1, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'CCC': {'K': 0, 'Y': 0, 'H': 1, 'P': 3, 'L': 1, 'Q': 0, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 1, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'CCG': {'K': 0, 'Y': 0, 'H': 0, 'P': 3, 'L': 1, 'Q': 1, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 1, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'CCT': {'K': 0, 'Y': 0, 'H': 1, 'P': 3, 'L': 1, 'Q': 0, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 1, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'CGA': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 1, 'Q': 1, 'V': 0, 'M': 0, 'R': 4, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 0, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'CGC': {'K': 0, 'Y': 0, 'H': 1, 'P': 1, 'L': 1, 'Q': 0, 'V': 0, 'M': 0, 'R': 3, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 1, 'C': 1, 'S': 1},
    'CGG': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 1, 'Q': 1, 'V': 0, 'M': 0, 'R': 4, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 1, 'G': 1, 'C': 0, 'S': 0},
    'CGT': {'K': 0, 'Y': 0, 'H': 1, 'P': 1, 'L': 1, 'Q': 0, 'V': 0, 'M': 0, 'R': 3, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 1, 'C': 1, 'S': 1},
    'CTA': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 4, 'Q': 1, 'V': 1, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 1, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'CTC': {'K': 0, 'Y': 0, 'H': 1, 'P': 1, 'L': 3, 'Q': 0, 'V': 1, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 0, 'F': 1, 'I': 1, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'CTG': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 4, 'Q': 1, 'V': 1, 'M': 1, 'R': 1, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'CTT': {'K': 0, 'Y': 0, 'H': 1, 'P': 1, 'L': 3, 'Q': 0, 'V': 1, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 0, 'F': 1, 'I': 1, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 0},
    'GAA': {'K': 1, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 1, 'V': 1, 'M': 0, 'R': 0, 'D': 2, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 1, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'GAC': {'K': 0, 'Y': 1, 'H': 1, 'P': 0, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 1, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 1, '*': 0, 'E': 2, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'GAG': {'K': 1, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 1, 'V': 1, 'M': 0, 'R': 0, 'D': 2, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 1, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'GAT': {'K': 0, 'Y': 1, 'H': 1, 'P': 0, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 1, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 1, '*': 0, 'E': 2, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'GCA': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 0, 'A': 3, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 1, 'W': 0, 'G': 1, 'C': 0, 'S': 1},
    'GCC': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 1, 'A': 3, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 1, 'C': 0, 'S': 1},
    'GCG': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 0, 'A': 3, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 1, 'W': 0, 'G': 1, 'C': 0, 'S': 1},
    'GCT': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 1, 'A': 3, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 1, 'C': 0, 'S': 1},
    'GGA': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 2, 'D': 0, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 1, 'W': 0, 'G': 3, 'C': 0, 'S': 0},
    'GGC': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 1, 'D': 1, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 3, 'C': 1, 'S': 1},
    'GGG': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 2, 'D': 0, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 1, 'W': 1, 'G': 3, 'C': 0, 'S': 0},
    'GGT': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 1, 'M': 0, 'R': 1, 'D': 1, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 3, 'C': 1, 'S': 1},
    'GTA': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 2, 'Q': 0, 'V': 3, 'M': 0, 'R': 0, 'D': 0, 'A': 1, 'T': 0, 'F': 0, 'I': 1, 'N': 0, '*': 0, 'E': 1, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'GTC': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 1, 'Q': 0, 'V': 3, 'M': 0, 'R': 0, 'D': 1, 'A': 1, 'T': 0, 'F': 1, 'I': 1, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'GTG': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 2, 'Q': 0, 'V': 3, 'M': 1, 'R': 0, 'D': 0, 'A': 1, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 0, 'E': 1, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'GTT': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 1, 'Q': 0, 'V': 3, 'M': 0, 'R': 0, 'D': 1, 'A': 1, 'T': 0, 'F': 1, 'I': 1, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 1, 'C': 0, 'S': 0},
    'TAA': {'K': 1, 'Y': 2, 'H': 0, 'P': 0, 'L': 1, 'Q': 1, 'V': 0, 'M': 0, 'R': 0, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 2, 'E': 1, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'TAC': {'K': 0, 'Y': 1, 'H': 1, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 1, 'A': 0, 'T': 0, 'F': 1, 'I': 0, 'N': 1, '*': 2, 'E': 0, 'W': 0, 'G': 0, 'C': 1, 'S': 1},
    'TAG': {'K': 1, 'Y': 2, 'H': 0, 'P': 0, 'L': 1, 'Q': 1, 'V': 0, 'M': 0, 'R': 0, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 1, 'W': 1, 'G': 0, 'C': 0, 'S': 1},
    'TAT': {'K': 0, 'Y': 1, 'H': 1, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 1, 'A': 0, 'T': 0, 'F': 1, 'I': 0, 'N': 1, '*': 2, 'E': 0, 'W': 0, 'G': 0, 'C': 1, 'S': 1},
    'TCA': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 1, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 0, 'A': 1, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 2, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 3},
    'TCC': {'K': 0, 'Y': 1, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 0, 'A': 1, 'T': 1, 'F': 1, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 1, 'S': 3},
    'TCG': {'K': 0, 'Y': 0, 'H': 0, 'P': 1, 'L': 1, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 0, 'A': 1, 'T': 1, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 0, 'W': 1, 'G': 0, 'C': 0, 'S': 3},
    'TCT': {'K': 0, 'Y': 1, 'H': 0, 'P': 1, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 0, 'D': 0, 'A': 1, 'T': 1, 'F': 1, 'I': 0, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 1, 'S': 3},
    'TGA': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 1, 'Q': 0, 'V': 0, 'M': 0, 'R': 2, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 1, 'E': 0, 'W': 1, 'G': 1, 'C': 2, 'S': 1},
    'TGC': {'K': 0, 'Y': 1, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 0, 'F': 1, 'I': 0, 'N': 0, '*': 1, 'E': 0, 'W': 1, 'G': 1, 'C': 1, 'S': 2},
    'TGG': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 1, 'Q': 0, 'V': 0, 'M': 0, 'R': 2, 'D': 0, 'A': 0, 'T': 0, 'F': 0, 'I': 0, 'N': 0, '*': 2, 'E': 0, 'W': 0, 'G': 1, 'C': 2, 'S': 1},
    'TGT': {'K': 0, 'Y': 1, 'H': 0, 'P': 0, 'L': 0, 'Q': 0, 'V': 0, 'M': 0, 'R': 1, 'D': 0, 'A': 0, 'T': 0, 'F': 1, 'I': 0, 'N': 0, '*': 1, 'E': 0, 'W': 1, 'G': 1, 'C': 1, 'S': 2},
    'TTA': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 2, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 0, 'A': 0, 'T': 0, 'F': 2, 'I': 1, 'N': 0, '*': 2, 'E': 0, 'W': 0, 'G': 0, 'C': 0, 'S': 1},
    'TTC': {'K': 0, 'Y': 1, 'H': 0, 'P': 0, 'L': 3, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 0, 'A': 0, 'T': 0, 'F': 1, 'I': 1, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 1, 'S': 1},
    'TTG': {'K': 0, 'Y': 0, 'H': 0, 'P': 0, 'L': 2, 'Q': 0, 'V': 1, 'M': 1, 'R': 0, 'D': 0, 'A': 0, 'T': 0, 'F': 2, 'I': 0, 'N': 0, '*': 1, 'E': 0, 'W': 1, 'G': 0, 'C': 0, 'S': 1},
    'TTT': {'K': 0, 'Y': 1, 'H': 0, 'P': 0, 'L': 3, 'Q': 0, 'V': 1, 'M': 0, 'R': 0, 'D': 0, 'A': 0, 'T': 0, 'F': 1, 'I': 1, 'N': 0, '*': 0, 'E': 0, 'W': 0, 'G': 0, 'C': 1, 'S': 1},
}

def calculate_codon_report(codon):
    # return value
    codon_report = {}
    
    # compute ref_residue
    ref_residue = translate(codon)
    
    # retrieve background rates
    background_rates = codon_background_rates[codon]
    
    # compute probabilities for mutations types
    codon_report['missense_probability'] = background_rates['missense'] / 9
    codon_report['synonymous_probability']  = background_rates['synonymous'] / 9
    codon_report['nonsense_probability']  = background_rates['nonsense'] / 9
    codon_report['nonsynonymous_probability']  = (background_rates['missense'] + background_rates['nonsense']) / 9
    
    # retrieve all alternative residues
    if ref_residue == '*':
        codon_report['missense_alt_residues'] = {}
    else:
        codon_report['missense_alt_residues'] = {key:(codon_background_residues[codon][key]/background_rates['missense']) for key in codon_background_residues[codon] if codon_background_residues[codon][key] > 0 and key != ref_residue and key != '*'}
        
    return codon_report

def calculate_background_residues_per_codon():
    codon_background_residues = {}
    
    for codon in translate_code:
        codon_background_residues[codon] = {residue:0 for residue in translate_residues}
    
    for codon in translate_code:
        for codon_pos in range(len(codon)):
            for nucleotide_base in nucleotide_bases:
                if codon[codon_pos] == nucleotide_base: continue
                
                alt_codon =""
                for i in range(len(codon)):
                    if i == codon_pos:
                        alt_codon+= nucleotide_base
                    else:
                        alt_codon+= codon[i]
                
                alt_residue = translate(alt_codon)
                
                codon_background_residues[codon][alt_residue] +=1
                
    # double check if the possibilities comply:
    for codon in codon_background_residues.keys():
        assert (np.sum([codon_background_residues[codon][key] for key in codon_background_residues[codon].keys()])) == 9
    
    
    # print it all
    print("{")
    for codon in sorted(codon_background_residues.keys()):
        print("\t'%s': %s," % (codon, codon_background_residues[codon]))
    print("}")
    
    return codon_background_residues

def calculate_background_rates_per_codon():
    codon_background_rates = {}
    
    for codon in translate_code:
        codon_background_rates[codon] = {'missense':0,'synonymous':0,'nonsense':0}
    
    for codon in translate_code:
        original_residue = translate(codon)
        
        for codon_pos in range(len(codon)):
            for nucleotide_base in nucleotide_bases:
                if codon[codon_pos] == nucleotide_base: continue
                
                alt_codon =""
                for i in range(len(codon)):
                    if i == codon_pos:
                        alt_codon+= nucleotide_base
                    else:
                        alt_codon+= codon[i]
                
                alt_residue = translate(alt_codon)
                
                if original_residue == alt_residue: codon_background_rates[codon]['synonymous'] +=1; continue
                elif original_residue != '*' and alt_residue == '*': codon_background_rates[codon]['nonsense'] +=1; continue
                elif original_residue == '*'and alt_residue != '*': codon_background_rates[codon]['nonsense'] +=1; continue
                elif original_residue != alt_residue: codon_background_rates[codon]['missense'] +=1; continue
                else:
                    raise Exception("This exception should not be possible")
    
    # double check if the possibilities comply:
    for codon in codon_background_rates.keys():
        assert (codon_background_rates[codon]['missense'] + codon_background_rates[codon]['nonsense'] + codon_background_rates[codon]['synonymous']) == 9
    
    
    # print it all
    print("{")
    for codon in sorted(codon_background_rates.keys()):
        print("\t'%s': %s," % (codon, codon_background_rates[codon]))
    print("}")
    
    return codon_background_rates

def calculate_CDS_background_rate(sequence):
    missense_total = 0
    nonsense_total = 0
    synonymous_total = 0
    
    assert (len(sequence)%3)==0 # check if sequence consists of triplets
    
    n = int(len(sequence) / 3)
    for i in range(0, n):
        codon = sequence[i * 3 : i * 3 + 3]
        missense_total += codon_background_rates[codon]['missense']
        nonsense_total += codon_background_rates[codon]['nonsense']
        synonymous_total += codon_background_rates[codon]['synonymous']
        
    return missense_total, nonsense_total, synonymous_total


