"""Prepare and summarize CMD monomer subfamily profile comparisons.

The intact 80--119-residue, explicitly CMD-annotated proteins are clustered
with MMseqs2 before profile construction.  This prevents unrelated CMD-like
lineages from being averaged into a single heterogeneous HH-suite profile.
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
from collections import defaultdict
from pathlib import Path

from Bio import SeqIO


ROOT = Path(__file__).parent
RESULTS = ROOT / "results"
MONOMERS = RESULTS / "cmd_single_monomer_80_119.fasta"
MEMBERSHIP = RESULTS / "cmd_single_monomer_cluster_cluster.tsv"
CLUSTER_DIR = RESULTS / "cmd_monomer_clusters"
MANIFEST = RESULTS / "cmd_monomer_cluster_manifest.tsv"
SUMMARY = RESULTS / "dehi_vs_cmd_monomer_clusters.tsv"
MIN_CLUSTER_SIZE = 5


def accession(record_id: str) -> str:
    fields = record_id.split("|")
    return fields[1] if len(fields) >= 3 else record_id


def read_membership() -> dict[str, list[str]]:
    members: dict[str, list[str]] = defaultdict(list)
    with MEMBERSHIP.open() as handle:
        for line in handle:
            representative, member = line.rstrip("\n").split("\t")
            members[representative].append(member)
    return members


def split_clusters() -> None:
    records = {
        accession(record.id): record for record in SeqIO.parse(MONOMERS, "fasta")
    }
    groups = [
        (representative, members)
        for representative, members in read_membership().items()
        if len(members) >= MIN_CLUSTER_SIZE
    ]
    groups.sort(key=lambda item: (-len(item[1]), item[0]))
    CLUSTER_DIR.mkdir(parents=True, exist_ok=True)

    with MANIFEST.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(
            [
                "cluster",
                "representative",
                "sequence_count",
                "minimum_length",
                "median_length",
                "maximum_length",
                "representative_description",
            ]
        )
        for number, (representative, member_ids) in enumerate(groups, start=1):
            cluster = f"CMD_monomer_{number:03d}"
            cluster_records = [records[member] for member in member_ids]
            lengths = [len(record.seq) for record in cluster_records]
            SeqIO.write(cluster_records, CLUSTER_DIR / f"{cluster}.fasta", "fasta")
            writer.writerow(
                [
                    cluster,
                    representative,
                    len(cluster_records),
                    min(lengths),
                    f"{statistics.median(lengths):g}",
                    max(lengths),
                    records[representative].description,
                ]
            )

    print(
        f"Wrote {len(groups)} CMD monomer clusters with at least "
        f"{MIN_CLUSTER_SIZE} sequences to {CLUSTER_DIR}"
    )


def parse_hhr(path: Path) -> dict[str, str | int | float]:
    text = path.read_text()
    detail = re.search(
        r"Probab=(\S+)\s+E-value=(\S+)\s+Score=(\S+)\s+"
        r"Aligned_cols=(\d+)\s+Identities=(\d+)%.*?Template_Neff=(\S+)",
        text,
    )
    query_length = re.search(r"^Match_columns\s+(\d+)", text, re.MULTILINE)
    result_line = next(
        (line for line in text.splitlines() if re.match(r"\s+1\s+", line)), None
    )
    template_length = (
        re.search(r"\((\d+)\)\s*$", result_line) if result_line is not None else None
    )
    if detail is None or query_length is None or template_length is None:
        raise ValueError(f"Could not parse HHalign result {path}")
    probability, evalue, score, columns, identity, neff = detail.groups()
    return {
        "probability": float(probability),
        "p_value": float(evalue),
        "score": float(score),
        "aligned_columns": int(columns),
        "identity_percent": int(identity),
        "query_model_length": int(query_length.group(1)),
        "template_model_length": int(template_length.group(1)),
        "template_neff": float(neff),
    }


def summarize() -> None:
    with MANIFEST.open() as handle:
        manifest = {
            row["cluster"]: row for row in csv.DictReader(handle, delimiter="\t")
        }

    rows = []
    for cluster, metadata in manifest.items():
        for half in ("N", "C"):
            path = CLUSTER_DIR / f"dehi_{half}_vs_{cluster}.hhr"
            result = parse_hhr(path)
            rows.append({"dehi_half": half, **metadata, **result, "hhr": str(path.relative_to(ROOT))})

    test_count = len(rows)
    for row in rows:
        row["bonferroni_p"] = min(1.0, float(row["p_value"]) * test_count)
        row["query_coverage_percent"] = (
            100 * int(row["aligned_columns"]) / int(row["query_model_length"])
        )
        row["template_coverage_percent"] = (
            100 * int(row["aligned_columns"]) / int(row["template_model_length"])
        )
    rows.sort(key=lambda row: (-float(row["probability"]), float(row["p_value"])))

    fieldnames = [
        "dehi_half",
        "cluster",
        "representative",
        "sequence_count",
        "minimum_length",
        "median_length",
        "maximum_length",
        "template_neff",
        "probability",
        "p_value",
        "bonferroni_p",
        "score",
        "aligned_columns",
        "identity_percent",
        "query_model_length",
        "template_model_length",
        "query_coverage_percent",
        "template_coverage_percent",
        "representative_description",
        "hhr",
    ]
    with SUMMARY.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Summarized {test_count} comparisons in {SUMMARY}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("split", "summarize"))
    args = parser.parse_args()
    if args.stage == "split":
        split_clusters()
    else:
        summarize()


if __name__ == "__main__":
    main()
