
=================
phon_query_to_csv
=================

	Batch combine and convert Phon query output to csv format for data analysis.

Overview
========

A Python package that takes the CSV files Phon exports from a query ("Table by
Session" listings, one file per session per analysis) and turns them into one
long analysis-ready dataset, plus an optional pivot table summary. It is built
on pandas and laid out as a PyScaffold package under ``src/phon_query_to_csv/``.

Setup
=====

The modules import each other by package name, so the package has to be
installed in the active environment (for example ``pip install -e .`` from the
repository root).

Dependencies are not declared in ``setup.cfg`` and must be installed by hand:

- ``pandas``
- ``numpy``
- ``ipa_features`` (imported by ``phone_data_expander.py``; appears to be the
  sibling repository of the same name, not a PyPI package)

Usage
=====

1. Open ``src/phon_query_to_csv/main.py`` and edit the three settings near the
   top of the ``__main__`` block:

   - ``directory``: folder containing the Phon query output
   - ``query``: name of the Phon query (e.g. ``"Queries_Target_v2"``,
     ``"Queries_Actual_v2"``), recorded in the ``Query Source`` column
   - ``flavor``: one of the presets listed below

2. Run ``main.py``. It asks whether to blank repeated labels in the pivot
   table, prints the parameters, and then prompts for the pivot table options.

3. Output is written to a ``Compiled/`` folder inside ``directory``.

Warning: ``overwrite`` defaults to ``True`` in ``main.py``, which deletes any
existing ``Compiled/`` folder in the data directory without asking. The
"Proceed? (y/n)" prompt does not currently stop the run (see Known issues).

Expected input
--------------

- Phon "Table by Session" CSV files with the columns ``Date``, ``Record #``,
  ``Group #``, ``Tier``, ``Range``, ``IPA Target``, ``IPA Actual``,
  ``Alignment``, ``Result``.
- Each file sits somewhere under a folder whose name contains the analysis
  (e.g. ``Initial Clusters Listing``, ``Final Singletons Listing``,
  ``Consonants Listing``, ``Vowels Listing``).
- Files with "Summary" in the name are skipped.

Where the metadata comes from
-----------------------------

- Participant and Phase: the flavor regexes, applied to the filename.
- Language: substrings of the filename (PEEP/En/eng for English, EFE/Sp/spa
  for Spanish, otherwise "Unspecified").
- Analysis: the name of the containing folder.
- Probe: the second underscore-separated piece of the filename.

Flavors
-------

A flavor is a preset pair of regexes for pulling participant ID and phase out
of filenames. It also sets whether target and actual are processed.

============  ==================  ================================================  ======  ======
Flavor        Participant regex   Phase regex                                       Target  Actual
============  ==================  ================================================  ======  ======
tx            ``\w\d\d\d``        ``BL-\d{1,2}|Post-\dmo|Pre|Post|Mid|Tx-\d{1,2}``  yes     yes
tx blind      ``\w(?=\d{4})``     ``\w{1}\d{4}``                                    yes     yes
typology      ``\d\d\d``          ``p[IVX]+``                                       no      yes
new typology  ``\w{3,4}\d\d``     none (no phases)                                  no      yes
itold         ``\w{4}\d{2}``      none (no phases)                                  yes     yes
ncjc          ``\w{1}\d{4}``      ``Timepoint\d|Pre|Post|Fall|Spring|Winter|...``   yes     yes
custom        prompted            prompted                                          asked   asked
============  ==================  ================================================  ======  ======

Pipeline
========

``main.py`` calls five steps in order.

1. ``gen_csv.py``: walks the directory and adds Participant, Phase, Language,
   Analysis and Probe columns to each Phon CSV. Also splits Phon's ``Result``
   string into Orthography, word-level IPA, Alignment and Notes.
   Output: ``Compiled/uniform_files/*.csv``

2. ``merge_csv.py``: concatenates the uniform files.
   Output: ``Compiled/merged_files/AllPart_AllLang_AllAnalyses_data.csv``

3. ``calculate_accuracy.py``: adds 0/1 Accuracy, Deletion and Substitution
   columns by comparing IPA Target with IPA Actual. Skipped when
   ``target=False``.
   Output: ``Compiled/merged_files/data_accuracy.csv``

4. ``phone_data_expander.py``: splits Target and Actual into up to three
   segments (T1-T3, A1-A3), each with base, voice, place, manner, sonority and
   EML, using ``ipa_features``.
   Output: ``Compiled/merged_files/full_annotated_dataset.csv``

5. ``create_pivot_table.py``: prompts for grouping variables, filters, value
   column and aggregation function, then writes a pivot table.
   Output: ``Compiled/merged_files/pivot_table_dataset.csv``

Other files
===========

Not part of the pipeline:

- ``sort_pivot_table.py``: sorts the pivot table output by accuracy. Merged
  (PR #12) but never called from ``main.py``.
- ``column_match.py``: optional step that renames and reorders columns
  according to ``column_alignment.csv``. Commented out of the pipeline.
- ``Phon_ipa_parse.py``, ``transcription_to_csv.py``, ``file_rename.py``,
  ``simple_csv_merge.py``: standalone utilities from 2020.
- ``skeleton.py``: PyScaffold boilerplate.
- ``test/``: two old single-file versions of the script.
- ``tests/``: sample Phon output only (two fixture sets,
  ``ssd_tx_target_test`` and ``typology_actual_test``). There are no actual
  tests.

History
=======

- 2020 to mid-2024 (Philip Combiths): core pipeline, the July 2024 restructure
  from a single script into this package, and the flavors.
- July-August 2025 (Francesco Vial): ``create_pivot_table.py`` (PR #11) and
  ``sort_pivot_table.py`` (PR #12).
- Since then (Philip Combiths): small changes only (tx blind flavor,
  blank-repeated-labels option, Compiled-directory check).

The remote also has about 20 other branches, mostly per-project forks (BESA,
ICPLA2023, SpSSDTx II/III, AdultDLD) plus a few unmerged feature branches such
as ``accuracy_panphon_edit_distance`` and ``refined_calculate_accuracy``.

Known issues
============

From a code read-through on 2026-11-14. The code was read but not run, so
these are unconfirmed until tested.

Likely bugs:

- Proceed prompt: the "Proceed? (y/n)" answer in ``main.py`` is ignored, so
  "n" still runs, and with ``overwrite=True`` that deletes ``Compiled/``.
- Flavor chain: in ``main.py``, ``tx`` is an ``if`` and ``tx blind`` starts a
  second ``if``/``elif`` chain. It works for the listed flavors, but a
  mistyped flavor falls through to an undefined-variable error.
- Target Type: ``phone_data_expander.py`` classifies C/CC/CCC by string
  length, so two-character affricates or any diacritic are misclassified.
- Sorting: ``sort_pivot_table`` sorts on a hardcoded ``Accuracy`` column and
  depends on the blanked-label layout, so it only works on the default pivot
  output. Its ``subdiv=[]`` default argument also carries over between calls.
- g replacement: step 1 replaces "g" with IPA "ɡ" in the segment columns
  only, not in the word-level columns.
- ``column_match.py`` uses an undefined ``directory`` variable and would fail
  if called.
- ``gen_csv.py`` returns ``set(probe_type)`` where ``set(probe_type_list)``
  was intended. Nothing uses that value at the moment.

Gaps:

- Dependencies are not declared in ``setup.cfg``.
- No automated tests.
- Five of the 52 fixture CSVs are in an older Phon export format without
  ``IPA Target`` / ``IPA Actual`` columns, and step 1 would fail on those.

Suggested next step: run the ``tx`` flavor against
``tests/ssd_tx_target_test/`` to confirm the pipeline still works end to end.
