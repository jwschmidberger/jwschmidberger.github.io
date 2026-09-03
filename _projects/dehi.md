---
title: "DehI internal duplication and CMD family relationships"
summary: "Structure-guided profile-HMM analysis of DehI evolution and its possible relationship to compact CMD proteins"
tech:
  - Bioinformatics
  - HH-suite
  - Profile HMMs
  - Structural biology
  - Quarto
links:
  - label: Interactive analysis report
    url: /projects/dehi-report/report.html
  - label: Analysis repository
    url: https://github.com/jwschmidberger/small_projects/tree/main/projects/dehi
---

DehI is a configuration-inverting 2-haloacid dehalogenase with two
structurally similar regions separated by a proline-rich linker. I used the
experimentally determined 3BJX structure to divide a 69-sequence DehI family
alignment into N- and C-terminal halves, then compared their HH-suite profile
hidden Markov models.

The two DehI profiles align across nearly their full lengths with **99.54%
HHalign probability**, supporting an ancient internal duplication despite only
17% direct sequence identity. A second analysis compares both repeats with
compact CMD and AhpD proteins. Clustering intact CMD monomers before profile
construction reveals several suggestive CMD subfamily matches that are hidden
in the pooled family alignment, although they remain below the threshold for a
confident family assignment.

[Open the complete illustrated analysis, methods, and downloadable results
&rarr;](/projects/dehi-report/report.html)
