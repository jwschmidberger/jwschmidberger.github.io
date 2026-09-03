"""Split the DehI family MSA into structural N- and C-terminal repeats.

The default 3BJX boundaries are native residues 1-129 (N repeat), 130-161
(proline-rich linker, excluded), and 162-296 (C repeat). The 3BJX alignment
record contains a 15-residue N-terminal expression tag, which is also excluded.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from Bio import AlignIO, SeqIO
from Bio.Align import MultipleSeqAlignment
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


def find_reference(alignment: MultipleSeqAlignment, reference_id: str) -> SeqRecord:
    matches = [record for record in alignment if record.id == reference_id]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one record with ID {reference_id!r}; found {len(matches)}"
        )
    return matches[0]


def residue_to_column(aligned_sequence: str) -> list[int]:
    """Return alignment columns indexed by zero-based ungapped residue index."""
    return [column for column, residue in enumerate(aligned_sequence) if residue not in "-."]


def remove_all_gap_columns(alignment: MultipleSeqAlignment) -> MultipleSeqAlignment:
    keep = [
        column
        for column in range(alignment.get_alignment_length())
        if any(str(record.seq)[column] not in "-." for record in alignment)
    ]
    records = []
    for record in alignment:
        sequence = "".join(str(record.seq)[column] for column in keep)
        records.append(
            SeqRecord(Seq(sequence), id=record.id, description=record.description)
        )
    return MultipleSeqAlignment(records)


def slice_alignment(
    alignment: MultipleSeqAlignment,
    start_column: int,
    end_column: int,
    region: str,
) -> MultipleSeqAlignment:
    records = []
    for record in alignment:
        sequence = str(record.seq)[start_column:end_column]
        records.append(
            SeqRecord(
                Seq(sequence),
                id=record.id,
                description=f"DehI_{region}_terminal_repeat",
            )
        )
    return remove_all_gap_columns(MultipleSeqAlignment(records))


def write_ungapped(alignment: MultipleSeqAlignment, destination: Path) -> int:
    records = []
    for record in alignment:
        sequence = str(record.seq).replace("-", "").replace(".", "")
        if sequence:
            records.append(
                SeqRecord(Seq(sequence), id=record.id, description=record.description)
            )
    return SeqIO.write(records, destination, "fasta")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "msa", nargs="?", type=Path, default=Path("results/dehi_core_msa.fasta")
    )
    parser.add_argument("--reference-id", default="3BJX")
    parser.add_argument(
        "--reference-prefix-length",
        type=int,
        default=15,
        help="Non-native residues before 3BJX residue 1 (default: expression tag of 15 aa)",
    )
    parser.add_argument("--linker-start", type=int, default=130)
    parser.add_argument("--linker-end", type=int, default=161)
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()

    if args.linker_start < 2 or args.linker_end < args.linker_start:
        raise ValueError("Invalid linker interval")

    alignment = AlignIO.read(args.msa, "fasta")
    reference = find_reference(alignment, args.reference_id)
    reference_columns = residue_to_column(str(reference.seq))

    # Convert one-based native 3BJX numbers into indices in the ungapped
    # alignment reference, accounting for the recombinant expression tag.
    n_start_index = args.reference_prefix_length
    linker_start_index = args.reference_prefix_length + args.linker_start - 1
    c_start_index = args.reference_prefix_length + args.linker_end
    if c_start_index >= len(reference_columns):
        raise ValueError(
            "The requested boundary lies beyond the ungapped 3BJX reference"
        )

    n_start_column = reference_columns[n_start_index]
    linker_start_column = reference_columns[linker_start_index]
    c_start_column = reference_columns[c_start_index]
    c_end_column = reference_columns[-1] + 1

    n_alignment = slice_alignment(
        alignment, n_start_column, linker_start_column, region="N"
    )
    c_alignment = slice_alignment(
        alignment, c_start_column, c_end_column, region="C"
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    n_msa_file = args.output_dir / "dehi_N_terminal_msa.fasta"
    c_msa_file = args.output_dir / "dehi_C_terminal_msa.fasta"
    n_sequence_file = args.output_dir / "dehi_N_terminal.fasta"
    c_sequence_file = args.output_dir / "dehi_C_terminal.fasta"
    report_file = args.output_dir / "dehi_terminal_split_report.tsv"

    AlignIO.write(n_alignment, n_msa_file, "fasta")
    AlignIO.write(c_alignment, c_msa_file, "fasta")
    n_count = write_ungapped(n_alignment, n_sequence_file)
    c_count = write_ungapped(c_alignment, c_sequence_file)

    with report_file.open("w") as handle:
        handle.write("region\treference_residues\tmsa_columns_1_based\talignment_length\tsequences\n")
        handle.write(
            f"N\t1-{args.linker_start - 1}\t{n_start_column + 1}-{linker_start_column}"
            f"\t{n_alignment.get_alignment_length()}\t{n_count}\n"
        )
        handle.write(
            f"linker_excluded\t{args.linker_start}-{args.linker_end}"
            f"\t{linker_start_column + 1}-{c_start_column}\tNA\tNA\n"
        )
        handle.write(
            f"C\t{args.linker_end + 1}-296\t{c_start_column + 1}-{c_end_column}"
            f"\t{c_alignment.get_alignment_length()}\t{c_count}\n"
        )

    print(f"Reference: {reference.id}")
    print(
        f"Excluded native linker residues {args.linker_start}-{args.linker_end} "
        f"({args.linker_end - args.linker_start + 1} aa)"
    )
    print(
        f"N repeat: residues 1-{args.linker_start - 1}; "
        f"{n_alignment.get_alignment_length()} aligned columns; {n_count} sequences"
    )
    print(
        f"C repeat: residues {args.linker_end + 1}-296; "
        f"{c_alignment.get_alignment_length()} aligned columns; {c_count} sequences"
    )
    print(f"Wrote {n_msa_file} and {c_msa_file}")
    print(f"Wrote {n_sequence_file} and {c_sequence_file}")
    print(f"Wrote {report_file}")


if __name__ == "__main__":
    main()
