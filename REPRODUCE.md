# Reproducing this study

Everything about running the study is in **[PROTOCOL.md](PROTOCOL.md)**: rebuilding the report from the stored
answers, regenerating the whole study from nothing, and extending it to more fixes or a longer period.

The short version:

```bash
python3 study.py doctor
```

```bash
python3 study.py rebuild
```

The first checks your setup. The second recomputes every number, chart and the report from the stored answers; if
`git status --short` then prints nothing, your rebuild matches what is published.

To check a single number, open the question script named under that finding in the README. Each is short and reads
only `dataset/`; [dataset/README.md](dataset/README.md) explains every file and column. To ask a new question, copy
a question script, change what it counts, and run it.
