"""Prepare interpretable CMD and AhpD sequence sets for profile comparison.

PF02627 spans the broader AhpD/CMD-like group despite its CMD name. To keep
the two operational groups separate, the CMD set retains records explicitly
annotated as carboxymuconolactone decarboxylase and excludes obvious fragments
and multidomain fusions. The AhpD set comes from the specific IPR004674
collection and receives a separate length filter.
"""

from pathlib import Path

from Bio import SeqIO
from Bio.Seq import Seq


RESULTS = Path(__file__).with_name("results")
CMD_INPUT = RESULTS / "uniprot_PF02627_nr60.fasta"
AHPD_INPUT = RESULTS / "uniprot_ahpd_IPR004674_nr60.fasta"
CMD_OUTPUT = RESULTS / "cmd_PF02627_nr60_curated.fasta"
AHPD_OUTPUT = RESULTS / "ahpd_IPR004674_nr60_curated.fasta"
REPORT = RESULTS / "cmd_ahpd_comparison_sets.tsv"
NONSTANDARD = str.maketrans({character: "X" for character in "BJOUZ*"})


def select_cmd(record) -> bool:
    description = record.description.lower()
    return (
        "carboxymuconolactone decarboxylase" in description
        and "ahpd" not in description
        and 80 <= len(record.seq) <= 220
    )


def select_ahpd(record) -> bool:
    return 120 <= len(record.seq) <= 230


def normalize_alphabet(records) -> int:
    substitutions = 0
    for record in records:
        sequence = str(record.seq).upper()
        normalized = sequence.translate(NONSTANDARD)
        substitutions += sum(left != right for left, right in zip(sequence, normalized))
        record.seq = Seq(normalized)
    return substitutions


def main() -> None:
    cmd_input = list(SeqIO.parse(CMD_INPUT, "fasta"))
    ahpd_input = list(SeqIO.parse(AHPD_INPUT, "fasta"))
    cmd = [record for record in cmd_input if select_cmd(record)]
    ahpd = [record for record in ahpd_input if select_ahpd(record)]
    cmd_substitutions = normalize_alphabet(cmd)
    ahpd_substitutions = normalize_alphabet(ahpd)

    SeqIO.write(cmd, CMD_OUTPUT, "fasta")
    SeqIO.write(ahpd, AHPD_OUTPUT, "fasta")

    with REPORT.open("w") as handle:
        handle.write("group\tsource\tinput_sequences\tretained_sequences\tmin_length\tmax_length\tnonstandard_to_X\n")
        handle.write(
            f"CMD-like\tPF02627 nr60, CMD annotation\t{len(cmd_input)}\t{len(cmd)}"
            f"\t{min(map(lambda r: len(r.seq), cmd))}\t{max(map(lambda r: len(r.seq), cmd))}"
            f"\t{cmd_substitutions}\n"
        )
        handle.write(
            f"AhpD\tIPR004674 nr60\t{len(ahpd_input)}\t{len(ahpd)}"
            f"\t{min(map(lambda r: len(r.seq), ahpd))}\t{max(map(lambda r: len(r.seq), ahpd))}"
            f"\t{ahpd_substitutions}\n"
        )

    print(f"CMD-like: retained {len(cmd)} of {len(cmd_input)} -> {CMD_OUTPUT}")
    print(f"AhpD: retained {len(ahpd)} of {len(ahpd_input)} -> {AHPD_OUTPUT}")
    print(f"Report: {REPORT}")


if __name__ == "__main__":
    main()
