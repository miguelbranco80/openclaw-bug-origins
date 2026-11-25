#!/usr/bin/env python3
"""Run every question script. Each writes results/<id>.json and its charts.

Usage: python3 questions/run_all.py
"""
import importlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    names = sorted(name[:-3] for name in os.listdir(HERE) if name.startswith("q") and name.endswith(".py"))
    for name in names:
        result = importlib.import_module(name).main(quiet=True)
        print(f"{name}: {len(result.rows)} numbers, {len(result.charts)} charts")


if __name__ == "__main__":
    main()
