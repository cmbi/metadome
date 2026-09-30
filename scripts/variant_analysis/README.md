# Variant analysis scripts
  
Analyses that annotate external variant sets against a published MetaDome data
release.
  
These read only files from the release, so they need no database, no prebuild
output and no running application. Anyone holding the Zenodo record can
reproduce the result with `bcftools` and `bedtools`.
  
## `clinvar_analysis.sh`
  
Finds ClinVar variants of uncertain significance that sit at positions where
homologous Pfam domains carry pathogenic missense variation, i.e. positions
where evidence can be transferred from another genomic position through homologous protein domains.
  
### Inputs
  
| Input | Source |
| --- | --- |
| `--clinvar` | ClinVar VCF for the assembly being analysed |
| `--release-dir` + `--prefix` | `_derived-track-pfam-domain-coverage.bed.gz`, `_derived-track-metadomain-clinvar.bed.gz` and `_final-dataset-sw10.tsv.gz` from the release |
| `--mapping-db` | `_prebuild-mapping-database.csv.gz` from the same release, which carries the MANE Select annotation. Its filename stem is shorter than the others, ending at the Pfam version |

The ClinVar VCF must match the assembly of the release; the two are joined on
genomic coordinates and nothing detects a mismatch.
  
### Running
  
```bash
./clinvar_analysis.sh \
    --release-dir  /path/to/release \
    --prefix       MetaDome_v2.0_GRCh38.p14_GENCODE-v45_UniProt-2025-01_Pfam-37.4_gnomAD-v4.1_ClinVar-2025-10-06 \
    --clinvar      /path/to/ClinVar/GRCh38/clinvar_20251006.vcf.gz \
    --mapping-db   /path/to/release/MetaDome_v2.0_GRCh38.p14_GENCODE-v45_UniProt-2025-01_Pfam-37.4_prebuild-mapping-database.csv.gz \
    --genome-build GRCh38.p14 \
    --out-dir      /path/to/output
```

`--clnsig` selects a different ClinVar significance class, so the same script
produces sensitivity arms over `Pathogenic/Likely_pathogenic` or
`Conflicting_classifications_of_pathogenicity`. `--mapping-db` supplies the
MANE Select annotation; without it `mane_select` is written as `NA`.
`--keep-intermediates` retains the BED files and raw intersects.
  
### Output
  
`vus_metadomain_<build>.tsv` holds one row per variant per domain placement,
restricted to variants with at least one homologous pathogenic or likely
pathogenic missense variant. Columns are the variant as ClinVar reports it,
then the MetaDome annotation: gene symbol, whether the placement is the one a
MANE Select transcript maps to, UniProt accession and position, Pfam accession
and consensus position, the homologous counts, the accessions behind those
counts, and a link to the position in MetaDome.
  
A variant covered by several domain placements or isoforms appears more than
once, so per-variant figures come from distinct `clinvar_id`, not row counts.
`mane_select` is `True` on the placement whose accession a MANE Select
transcript maps to, so filtering on it reduces the table to the placements a
MANE Select transcript reports. It is `False` throughout GRCh37, where GENCODE
v19 predates MANE.
  
`vus_metadomain_<build>_summary.tsv` records the counts the table cannot: how
many variants were selected, and how many fall inside a Pfam domain. Variants
without homologous evidence are excluded from the table, so its denominators
live here. With `--mapping-db` it also records the number of MANE Select
accessions and the same denominators restricted to them.
  
### Coordinates
  
The release tracks are 0-based half-open BED, so `bedtools` reads them directly
and no conversion is applied.
  
The script verifies this held. A codon's own ClinVar records are excluded from
its homologous counts when the release is built, so a variant must never appear
among its own accessions. The reported `self-contamination` count must be zero;
anything else means the intersects are misaligned and the output should be
discarded.

## `plot_clinvar_analysis.py`
  
Draws a plotted figure from the output of `clinvar_analysis.sh` for one genome build, over all placements or over MANE Select placements only.

### Running
  
`pandas`, `seaborn` and `matplotlib` are not application dependencies and are
not in `requirements.txt`. `Dockerfile_plots` provides them:
  
```bash
docker build -f Dockerfile_plots -t metadome-plots .
  
docker run --rm -u "$(id -u):$(id -g)" \
    -v /path/to/output:/work -v "$PWD:/scripts:ro" metadome-plots \
    python /scripts/plot_clinvar_analysis.py \
        --table vus_metadomain_GRCh38.p14.tsv \
        --summary vus_metadomain_GRCh38.p14_summary.tsv \
        --genome-build GRCh38.p14 \
        --counts
```

`-u` keeps the output owned by the invoking user rather than root. `/work` is
the directory holding the tables, so `--table` and `--summary` are relative to
it and the figures are written beside them.

`--mane-only` restricts both panels to placements whose accession is the one a
MANE Select transcript maps to, reading `mane_select` from the table and
`distinct_vus_in_domain_mane` from the summary. GENCODE v19 carries no MANE
transcripts, so it is meaningful only for GRCh38.

### Output
  
`vus_metadomain_<build>.pdf`, `.png` and `.svg` at 300 dpi. `--out-stem`
replaces `vus_metadomain_<build>` with a name of your own, so several figures
can be written into one directory. `--counts` additionally writes
`<stem>_panelB_counts.tsv`, the raw counts behind panel B, which partition the
candidate set.

Those counts are the check: they are computed by pandas and must match the
counts `clinvar_analysis.sh` reports.
