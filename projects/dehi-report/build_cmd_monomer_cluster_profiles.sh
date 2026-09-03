#!/usr/bin/env bash
# Cluster intact CMD monomers, build one HHM per coherent subfamily, and compare
# each profile independently with the N- and C-terminal DehI profiles.

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
results_dir="${script_dir}/results"
project_root="$(cd "${script_dir}/../.." && pwd)"
python_cmd="${PYTHON:-${project_root}/.venv/bin/python}"
cluster_dir="${results_dir}/cmd_monomer_clusters"

for program in mmseqs mafft reformat.pl hhmake hhalign; do
    if ! command -v "${program}" >/dev/null 2>&1; then
        echo "ERROR: ${program} is not on PATH." >&2
        exit 1
    fi
done

"${python_cmd}" "${script_dir}/identify_cmd_ahpd_duplications.py" prepare
if [[ ! -s "${results_dir}/cmd_single_monomer_cluster_cluster.tsv" ]]; then
    mmseqs easy-cluster \
        "${results_dir}/cmd_single_monomer_80_119.fasta" \
        "${results_dir}/cmd_single_monomer_cluster" \
        "${results_dir}/mmseqs_monomer_tmp" \
        --min-seq-id 0.30 -c 0.70 --cov-mode 0 --threads 4
else
    echo "Reusing existing MMseqs2 monomer clusters."
fi
"${python_cmd}" "${script_dir}/analyse_cmd_monomer_clusters.py" split

while IFS=$'\t' read -r cluster representative sequence_count rest; do
    if [[ "${cluster}" == "cluster" ]]; then
        continue
    fi
    mafft --thread 1 --retree 1 --maxiterate 0 \
        "${cluster_dir}/${cluster}.fasta" \
        > "${cluster_dir}/${cluster}_msa.fasta"
    reformat.pl fas a3m \
        "${cluster_dir}/${cluster}_msa.fasta" \
        "${cluster_dir}/${cluster}.a3m" -M 50
    hhmake -i "${cluster_dir}/${cluster}.a3m" \
        -o "${cluster_dir}/${cluster}.hhm" -name "${cluster}"

    for half in N C; do
        hhalign \
            -i "${results_dir}/dehi_${half}_terminal.hhm" \
            -t "${cluster_dir}/${cluster}.hhm" \
            -o "${cluster_dir}/dehi_${half}_vs_${cluster}.hhr"
    done
done < "${results_dir}/cmd_monomer_cluster_manifest.tsv"

# The three lead subfamilies are compared post hoc to determine whether the
# independent DehI hits arise from a coherent CMD lineage. These comparisons
# are supporting diagnostics, not independent tests of DehI homology.
hhalign -i "${cluster_dir}/CMD_monomer_015.hhm" \
    -t "${cluster_dir}/CMD_monomer_017.hhm" \
    -o "${cluster_dir}/CMD_monomer_015_vs_017.hhr"
hhalign -i "${cluster_dir}/CMD_monomer_015.hhm" \
    -t "${cluster_dir}/CMD_monomer_003.hhm" \
    -o "${cluster_dir}/CMD_monomer_015_vs_003.hhr"
hhalign -i "${cluster_dir}/CMD_monomer_017.hhm" \
    -t "${cluster_dir}/CMD_monomer_003.hhm" \
    -o "${cluster_dir}/CMD_monomer_017_vs_003.hhr"

"${python_cmd}" "${script_dir}/analyse_cmd_monomer_clusters.py" summarize
echo "Built and ranked intact CMD monomer subfamily profiles in ${cluster_dir}"
