#!/bin/sh
# Rebuild every derived file, the charts and the README from the data in this repository.
# Needs Python 3 only: no network, no git history, no model access.
# If nothing was changed, `git status` afterwards shows no modified files.
set -e
cd "$(dirname "$0")"
F=fix-origins
P=$F/review-pilot

# 1. From the models' stored answers to per-case files (in the collection folders).
python3 $F/clawsweeper/assemble_results.py >/dev/null       # review table + readers' verdicts
python3 $P/select_cases.py >/dev/null     # the 30 blind-review cases
python3 $P/grade_bundles.py $P/data/runs $P/data/grade >/dev/null   # reviewers' raw output -> blind grading bundles
mv $P/data/grade/findings.jsonl $P/findings.jsonl
python3 $P/assemble_results.py >/dev/null                   # unblind the grades
python3 $P/verify_tabulate.py $P/data/verify $P/data/grade/grid.json >/dev/null   # checks on reported problems
python3 $P/verify_control.py >/dev/null                     # the checkers' control
python3 $F/audit/collect.py $F/audit/raw $P/data/grade/key.json $P/data/grade/grid.json >/dev/null  # second-model re-reads

python3 $F/comparison/build_changes.py >/dev/null           # fetched pull request facts -> dataset/changes.jsonl

# 2. The dataset: the facts every question reads.
python3 dataset/build.py >/dev/null

# 3. One script per question: numbers into results/, charts into charts/.
python3 questions/run_all.py

# 4. The report.
python3 report/render.py
echo "Rebuilt. Run 'git status --short' to see whether anything changed."
