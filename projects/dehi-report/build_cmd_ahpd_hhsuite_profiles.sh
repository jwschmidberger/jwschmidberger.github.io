#!/usr/bin/env bash
# Align curated CMD/AhpD sets, build HH-suite profiles, and compare with DehI.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
results_dir="${script_dir}/results"

for program in mafft reformat.pl hhmake hhalign; do
    if ! command -v "${program}" >/dev/null 2>&1; then
        echo "ERROR: ${program} is not on PATH." >&2
        exit 1
    fi
done

python_cmd="${PYTHON:-python}"
"${python_cmd}" "${script_dir}/prepare_cmd_ahpd_comparison.py"

cmd_fasta="${results_dir}/cmd_PF02627_nr60_curated.fasta"
ahpd_fasta="${results_dir}/ahpd_IPR004674_nr60_curated.fasta"
cmd_msa="${results_dir}/cmd_PF02627_nr60_msa.fasta"
ahpd_msa="${results_dir}/ahpd_IPR004674_nr60_msa.fasta"
cmd_a3m="${results_dir}/cmd_PF02627_nr60.a3m"
ahpd_a3m="${results_dir}/ahpd_IPR004674_nr60.a3m"
cmd_hhm="${results_dir}/cmd_PF02627_nr60.hhm"
ahpd_hhm="${results_dir}/ahpd_IPR004674_nr60.hhm"

# Fast FFT-NS-1 is appropriate for these already redundancy-reduced families.
mafft --thread -1 --retree 1 --maxiterate 0 "${cmd_fasta}" > "${cmd_msa}"
mafft --thread -1 --retree 1 --maxiterate 0 "${ahpd_fasta}" > "${ahpd_msa}"

reformat.pl fas a3m "${cmd_msa}" "${cmd_a3m}" -M 50
reformat.pl fas a3m "${ahpd_msa}" "${ahpd_a3m}" -M 50

hhmake -i "${cmd_a3m}" -o "${cmd_hhm}" -name CMD_PF02627_non_AhpD
hhmake -i "${ahpd_a3m}" -o "${ahpd_hhm}" -name AhpD_IPR004674

compare() {
    local query_name="$1"
    local query_hhm="$2"
    local target_name="$3"
    local target_hhm="$4"
    local stem="${results_dir}/${query_name}_vs_${target_name}"
    hhalign -i "${query_hhm}" -t "${target_hhm}" \
        -o "${stem}.hhr" -Oa3m "${stem}.a3m" -atab "${stem}.tsv"
}

compare "dehi_N" "${results_dir}/dehi_N_terminal.hhm" "CMD" "${cmd_hhm}"
compare "dehi_C" "${results_dir}/dehi_C_terminal.hhm" "CMD" "${cmd_hhm}"
compare "dehi_N" "${results_dir}/dehi_N_terminal.hhm" "AhpD" "${ahpd_hhm}"
compare "dehi_C" "${results_dir}/dehi_C_terminal.hhm" "AhpD" "${ahpd_hhm}"
compare "CMD" "${cmd_hhm}" "AhpD" "${ahpd_hhm}"

echo "Built CMD and AhpD HHMs and five HHalign comparisons in ${results_dir}"
