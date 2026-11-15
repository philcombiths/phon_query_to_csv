# TODO

From a structural code review on 2026-11-14. The code was read, not run (the
`ipa_features` dependency was not installed in the review environment), so each
bug below should be confirmed against the fixtures in `tests/` before fixing.
Background on the pipeline and the shorter "Known issues" list is in
`README.rst`.

Items are ordered by priority within each section. Line numbers refer to files
under `src/phon_query_to_csv/` as of commit `0c1b449`.

## 1. Data safety (fix first)

- [ ] Make the "Proceed? (y/n)" prompt actually stop the run. The answer is
      discarded at `main.py:128`, so answering "n" still runs the pipeline.
- [ ] Change the `overwrite` default in `main.py:57` to `False`, or ask before
      deleting. With `overwrite=True`, `gen_csv.py:65-68` removes an existing
      `Compiled/` folder with no confirmation. Combined with the item above,
      there is currently no way to back out once the script starts.
- [ ] Move the hardcoded data path out of `main.py:64` (currently a lab share
      path under a lab member's folder). Take `directory`, `query` and `flavor`
      as command-line arguments or from a small config file that is not
      committed, so running the script does not require editing source.

## 2. Bugs that can silently change the data

- [ ] Language detection by substring (`gen_csv.py:140-157`). The keys `En` and
      `Sp` match unrelated text, and English keys are checked first.
      - `Sp` matches `Spring`, which is one of the `ncjc` phase names, so an
        NCJC file from a spring timepoint with no other language marker is
        labeled Spanish.
      - The fixture `Spanish.S201_EFE-B-Little-PEEP-V2_Post-1mo_REVISED.csv`
        contains both `PEEP` and `EFE` and comes out as English. Decide
        whether that is intended (probe language) or wrong (session language),
        then document the rule.
      - Suggested fix: match on a delimited token or on the filename prefix
        (`English.` / `Spanish.` / `eng.` / `span.`) rather than a bare
        substring.
- [ ] Uniform file name collisions (`gen_csv.py:241-249`). Output files are
      named from participant, language, phase, analysis, probe and probe type.
      Two input files that share all six (for example an original and a
      `_REVISED` export of the same session) write to the same path and the
      first is overwritten without warning. Check for an existing file before
      writing, or include the source filename.
- [ ] Merge assumes identical columns (`merge_csv.py:134-139`). Files are
      concatenated as raw bytes with the header dropped from all but the
      first. If any uniform file has different columns or column order, its
      rows are shifted into the wrong columns with no error. Replace with
      `pd.concat` over `pd.read_csv`, which aligns by column name. This also
      makes row order deterministic (`glob` order is not guaranteed).
- [ ] `Target Type` uses string length (`phone_data_expander.py:104-108`).
      Affricates and anything with a diacritic are misclassified, empty
      targets become `CCC`, and vowel analyses are labeled `C`. Use
      `Target Num Segs` from `ipa_features` instead, and leave the column
      blank for non-consonant analyses.
- [ ] Segment count is capped at 3 (`phone_data_expander.py:55-72`). The
      counter only advances inside the loop over three segment slots, so a
      four-segment string reports `Num Segs = 3` and the extra segment is
      dropped silently. Count all segments, and log when one is truncated.
- [ ] Blanked labels in the pivot table (`create_pivot_table.py:146-154`).
      Each column is blanked independently against the previous row, so a
      nested label is blanked even when its parent changed (participant B's
      first `Pre` row loses its Phase label if participant A's last row was
      also `Pre`). Blank a label only when all columns to its left are also
      unchanged.
- [ ] `g` to IPA `ɡ` replacement covers only the segment columns
      (`gen_csv.py:226-231`), not `IPA Target Words`, `IPA Actual Words` or
      the alignment columns. Apply consistently.
- [ ] Accuracy edge cases (`calculate_accuracy.py:27-32`). Decide and document
      the intended coding for:
      - target empty, actual present (currently Substitution = 1; there is no
        addition/epenthesis category)
      - both empty (currently Deletion = 1, Accuracy = 0)
      - visually identical strings that differ in Unicode normalization
        (currently inaccurate; consider normalizing both columns first)

## 3. Bugs that crash or misreport

- [ ] Flavor selection (`main.py:74-114`). `tx` is a standalone `if` and
      `tx blind` begins a separate `if`/`elif` chain. Make it one chain with a
      final `else` that reports the unknown flavor; right now a typo ends in a
      `NameError` on `phase_re`. A dict of flavor presets would be simpler
      and would let the README table be generated from one place.
- [ ] Success messages print even on failure (`main.py:47-48`).
      `create_pivot_table` returns `None` on every path, including its error
      exits, so "pivot_table_dataset.csv generated successfully" is printed
      regardless. Return the output path (or raise) and check it.
- [ ] `phon_query_to_csv()` returns `None` because of the above. Return the
      annotated DataFrame or the output paths.
- [ ] Analysis lookup (`gen_csv.py:119-122`). A CSV in a folder whose path has
      no recognized analysis name raises a bare `IndexError`. Raise a message
      that names the file, as is already done for participant.
- [ ] Older Phon export format. Five of the 52 fixture CSVs have the header
      `Date, Group #, Tier, Range, Result` with no `IPA Target` / `IPA Actual`
      columns, and step 1 fails on them with a `KeyError`. Either support the
      old format (the commented-out lambdas at `gen_csv.py:193-200` did this)
      or skip such files with a warning.
- [ ] `Probe` picks up the file extension (`gen_csv.py:181`). When the
      filename has only one underscore (all typology fixtures, e.g.
      `span.009span_pI.csv`), `Probe` becomes `pI.csv`. Strip the extension
      before splitting. `Probe Type` is just a copy of `Phase`
      (`gen_csv.py:186`); decide what it should hold or drop it. This is the
      existing "fix Probe Type and Probe columns" note in `main.py`.
- [ ] `ID-Target-Lang` (`phone_data_expander.py:98`) lacks the `.astype(str)`
      that `ID-Actual-Lang` has on line 75, so it fails if participant IDs are
      read back as numbers.
- [ ] `log.info("Saved", outfile)` at `merge_csv.py:142` passes an argument
      with no format placeholder, which makes `logging` print a traceback to
      the console on every run. Also remove the no-op `csv.writer(outfile)`
      on line 141.
- [ ] `gen_csv.py:264` returns `set(probe_type)` (the characters of one
      string) where `set(probe_type_list)` was meant. The docstring also
      describes a 5-tuple while the function returns 8 values.
- [ ] The `Compiled` / `.bak` skip at `gen_csv.py:74` is a substring test on
      the full path, so a data directory whose own path contains "Compiled"
      is skipped entirely and produces an empty result.
- [ ] `column_match.py:105` uses an undefined `directory`, and line 84
      compares an int to a list. Fix or remove the module (see section 6).
- [ ] `sort_pivot_table.py`: `subdiv=[]` mutable default (line 26) carries
      results over between calls; sorting is hardcoded to an `Accuracy`
      column (lines 74, 76) and to the blanked-label layout. Either
      generalize it and call it from `main.py`, or mark it experimental.

## 4. Packaging and setup

- [ ] Declare dependencies in `setup.cfg` under `install_requires`: `pandas`,
      `numpy`, and `ipa_features` (as a Git URL dependency, since it is the
      sibling repository and not on PyPI). A fresh `pip install -e .`
      currently installs none of them.
- [ ] Replace the PyScaffold placeholders in `setup.cfg`: `description`
      ("Add a short description here!"), `url` and `project_urls` (still
      pointing at pyscaffold.org).
- [ ] Add a console entry point under `[options.entry_points]` once `main.py`
      takes arguments, so the tool runs as a command.
- [ ] `logging_config.py` opens `phon_query_to_csv.log` in the current working
      directory at import time, once per module. Configure logging once in
      `main.py` and write the log into `Compiled/`. This covers the existing
      "Clean up logging" note.

## 5. Tests

- [ ] Add an end-to-end test for the `tx` flavor on `tests/ssd_tx_target_test/`
      and one for `typology` on `tests/typology_actual_test/`, run against a
      temporary copy so `Compiled/` is not written into the repo. Doing this
      first will confirm or rule out most of sections 2 and 3.
- [ ] Add unit tests for the pieces with the most logic: filename metadata
      extraction for each flavor, the `Result` string split, accuracy coding,
      and pivot label blanking.
- [ ] `create_pivot_table` and `main.py` call `input()` directly. Pass the
      choices in as arguments (the function signatures already allow it) so
      the pipeline can run unattended in tests.
- [ ] `setup.cfg` configures `pytest --cov`, but `tests/` has only a dummy
      `conftest.py`.

## 6. Repository cleanup

- [ ] Untrack the 30 committed `.DS_Store` files and `.Rhistory`
      (`git rm --cached`). `.DS_Store` is already in `.gitignore`; add
      `.Rhistory`.
- [ ] Decide what to do with code outside the pipeline: `skeleton.py`
      (PyScaffold boilerplate), `inspiration/regex_compiler.py`,
      `Phon_ipa_parse.py`, `transcription_to_csv.py`, `file_rename.py`,
      `simple_csv_merge.py`, the two legacy scripts in `test/`, and
      `rev_csv.csv`. Suggest moving anything worth keeping into a `legacy/`
      folder and deleting the rest. Having both `test/` and `tests/` is
      confusing.
- [ ] `enter_dir` in `context_manager.py` is imported by `gen_csv.py` but never
      used. Remove it, and consider dropping the `chdir` in `gen_csv`
      altogether since every path is already joined to `directory`.
- [ ] Review the roughly 20 remote branches. Per-project forks (BESA,
      ICPLA2023, SpSSDTx II/III, AdultDLD) could become flavors on `master`;
      `accuracy_panphon_edit_distance` and `refined_calculate_accuracy` may
      hold work relevant to the accuracy items in section 2.
- [ ] Fill in `CHANGELOG.rst` and `AUTHORS.rst` (add Francesco Vial).
- [ ] The docstring in `main.py:16` names the final file
      `full_accuracy_dataset.csv`; the code writes
      `full_annotated_dataset.csv`.

## 7. Existing notes carried over from the code

These were already written as `TODO` comments and are not covered above.

- [ ] Add an Error Score column (`main.py:2`).
- [ ] Remove intermediate files after a run (`main.py:4`).
- [ ] Make column identification generic and robust to different filename
      patterns (`main.py:5`).
- [ ] Handle vowel and diacritic features (`phone_data_expander.py:81`).
- [ ] Draw on other tables, including baseline phones, for additional columns
      (`phone_data_expander.py:9`).

## Suggested README changes

`README.rst` was left untouched. Once the items above are addressed:

- Remove the corresponding entries from its "Known issues" section.
- Add the language-detection rule and the Probe / Probe Type definitions once
  they are decided.
- Add a short example of one input filename per flavor and the metadata it
  yields.
