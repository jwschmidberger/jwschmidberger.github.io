#!/usr/bin/env bash
# Build HH-suite profiles for the two DehI repeats and compare them with HHalign.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
results_dir="${script_dir}/results"

for program in reformat.pl hhmake hhalign; do
    if ! command -v "${program}" >/dev/null 2>&1; then
        echo "ERROR: ${program} is not on PATH. Install HH-suite 3 first." >&2
        exit 1
    fi
done

n_msa="${results_dir}/dehi_N_terminal_msa.fasta"
c_msa="${results_dir}/dehi_C_terminal_msa.fasta"
n_a3m="${results_dir}/dehi_N_terminal.a3m"
c_a3m="${results_dir}/dehi_C_terminal.a3m"
n_hhm="${results_dir}/dehi_N_terminal.hhm"
c_hhm="${results_dir}/dehi_C_terminal.hhm"
comparison="${results_dir}/dehi_N_vs_C.hhr"
pairwise="${results_dir}/dehi_N_vs_C.a3m"
table="${results_dir}/dehi_N_vs_C.tsv"

# Define match states as columns occupied in at least 50% of family members.
# Remaining residues become lower-case insert states in A3M format.
reformat.pl fas a3m "${n_msa}" "${n_a3m}" -M 50
reformat.pl fas a3m "${c_msa}" "${c_a3m}" -M 50

hhmake -i "${n_a3m}" -o "${n_hhm}" -name DehI_N_terminal
hhmake -i "${c_a3m}" -o "${c_hhm}" -name DehI_C_terminal

# Local HMM-HMM comparison is the sensitive default for remote repeat homology.
hhalign \
    -i "${n_hhm}" \
    -t "${c_hhm}" \
    -o "${comparison}" \
    -Oa3m "${pairwise}" \
    -atab "${table}"

echo "Built ${n_hhm}"
echo "Built ${c_hhm}"
echo "HHalign report: ${comparison}"
echo "Pairwise profile alignment: ${pairwise}"
echo "Tabular alignment: ${table}"
