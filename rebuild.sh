#!/bin/sh
# Rebuild every derived file and the README from the data in this repository.
# Needs Python 3 only: no network, no git history, no model access.
# If nothing was changed, `git status` afterwards shows no modified files.
set -e
cd "$(dirname "$0")"
F=fix-origins
P=$F/review-pilot

python3 $F/clawsweeper/assemble_results.py                 # review table + readers' verdicts -> clawsweeper/results.jsonl
python3 $P/select_cases.py --skip 53,113,176 >/dev/null    # the 30 pilot cases (see the script for the skipped three)
python3 $P/grade_bundles.py $P/data/runs $P/data/grade      # reviewers' raw output -> findings + blind grading bundles
mv $P/data/grade/findings.jsonl $P/findings.jsonl
python3 $P/assemble_results.py                              # grades -> review-pilot/results.jsonl
python3 $P/verify_tabulate.py $P/data/verify $P/data/grade/grid.json >/dev/null   # checks on reported problems
python3 $P/verify_control.py                                # the checkers' control
python3 $F/audit/collect.py $F/audit/raw $P/data/grade/key.json $P/data/grade/grid.json >/dev/null  # second-model re-reads
python3 $F/audit/size_and_route.py >/dev/null               # first look: size and route
python3 $F/dashboard/build_data.py                          # the five data files behind the report
python3 $F/dashboard/render_readme.py                       # README.md
echo "Rebuilt. Run 'git status --short' to see whether anything changed."
