"""
Master ETL Pipeline Runner
Executes the full pipeline: Generation -> Cleaning -> Validation -> Transformation -> DB Sync.
"""

import sys
import os
import time
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from pipeline.ingestion.generator import generate_all_data
from pipeline.ingestion.loader import load_raw_data
from pipeline.cleaning.cleaner import clean_all
from pipeline.validation.validator import validate
from pipeline.transformation.metrics import compute_all_metrics
from pipeline.transformation.scoring import calculate_scores
from pipeline.database.db import get_db

def run_pipeline(generate=False, load_db=True):
    start = time.time()
    print("\n" + "="*65)
    print("  VENDOR PERFORMANCE & PROCUREMENT INTELLIGENCE - ETL PIPELINE")
    print("="*65)

    raw_path = os.path.join(BASE_DIR, 'data', 'raw', 'purchases_raw.csv')
    if generate or not os.path.exists(raw_path):
        print("\n>>> [1/5] GENERATING REALISTIC ENTERPRISE DATASET")
        generate_all_data()
    else:
        print("\n>>> [1/5] RAW DATASET VERIFIED")

    print("\n>>> [2/5] INGESTION & DATA CLEANING")
    raw_data = load_raw_data()
    cleaned = clean_all(raw_data)

    print("\n>>> [3/5] STRUCTURAL & REFERENTIAL VALIDATION")
    val_res = validate(cleaned)
    if val_res['status'] != 'PASSED':
        print("[-] Pipeline validation checks failed!")
        sys.exit(1)

    print("\n>>> [4/5] ANALYTICS & VENDOR PERFORMANCE SCORING")
    summary = compute_all_metrics(cleaned)
    scores = calculate_scores(summary)

    if load_db:
        print("\n>>> [5/5] RELATIONAL DATABASE SYNC (STAR SCHEMA)")
        db = get_db()
        db.load_star_schema()

    elapsed = round(time.time() - start, 2)
    print("\n" + "="*65)
    print(f" [+] PIPELINE EXECUTION COMPLETED IN {elapsed} SECONDS!")
    print("="*65 + "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--generate', action='store_true')
    parser.add_argument('--no-db', action='store_true')
    args = parser.parse_args()

    run_pipeline(generate=(args.all or args.generate), load_db=not args.no_db)
