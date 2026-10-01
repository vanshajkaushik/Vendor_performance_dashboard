"""
Vendor Performance Analytics - Master ETL Pipeline Orchestrator
Executes the complete end-to-end data lifecycle:
Raw Generation -> Ingestion -> Cleaning -> Validation -> Transformation -> DB Loading.
"""

import sys
import os
import time
import argparse

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.ingestion.generator import generate_synthetic_data
from src.ingestion.loader import load_raw_data, inspect_raw_schemas
from src.cleaning.cleaner import clean_all_datasets
from src.validation.validator import validate_datasets, generate_data_quality_report
from src.transformation.metrics import calculate_all_metrics
from src.transformation.scoring import calculate_vendor_scores
from src.database.db import get_db_manager

def run_pipeline(generate=False, clean=True, validate=True, transform=True, load_db=True):
    start_time = time.time()
    print("\n" + "="*60)
    print("  VENDOR PERFORMANCE ANALYTICS - END-TO-END DATA PIPELINE")
    print("="*60)

    # Step 1: Synthetic Data Generation (if requested or raw data missing)
    raw_purchases_path = os.path.join(BASE_DIR, 'data', 'raw', 'purchases_raw.csv')
    if generate or not os.path.exists(raw_purchases_path):
        print("\n>>> [STEP 1/5] GENERATING SYNTHETIC DATASETS (10,000+ ROWS)")
        generate_synthetic_data()
    else:
        print("\n>>> [STEP 1/5] RAW DATASETS DETECTED (Skipping generation)")

    # Step 2: Ingestion & Schema Inspection
    print("\n>>> [STEP 2/5] INGESTION & SCHEMA INSPECTION")
    raw_data = load_raw_data()
    inspect_raw_schemas(raw_data)

    # Step 3: Cleaning & Standardization
    if clean:
        print("\n>>> [STEP 3/5] EXECUTING DATA CLEANING PIPELINE")
        cleaned_data = clean_all_datasets(raw_data)
    else:
        print("Skipping cleaning")
        return

    # Step 4: Data Validation & Quality Report
    if validate:
        print("\n>>> [STEP 4/5] DATA VALIDATION & QUALITY ENFORCEMENT")
        val_results = validate_datasets(cleaned_data)
        generate_data_quality_report(val_results)
        if val_results['status'] != 'PASSED':
            print("[-] Data validation failed! Halting pipeline.")
            sys.exit(1)

    # Step 5: Analytical Transformation & Scoring
    if transform:
        print("\n>>> [STEP 5/5] ANALYTICAL METRICS & VENDOR PERFORMANCE SCORING")
        metrics = calculate_all_metrics(cleaned_data)
        scores = calculate_vendor_scores(metrics['vendor_summary'])

    # Step 6: Database Ingestion (PostgreSQL / SQLite)
    if load_db:
        print("\n>>> [DATABASE LOAD] SYNCING PROCESSED TABLES TO SQL ENGINE")
        db = get_db_manager()
        db.load_processed_tables()

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "="*60)
    print(f" [+] PIPELINE COMPLETED SUCCESSFULLY IN {elapsed}s!")
    print("="*60 + "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Vendor Performance Analytics Pipeline")
    parser.add_argument('--all', action='store_true', help="Run all pipeline stages including generation")
    parser.add_argument('--generate', action='store_true', help="Regenerate synthetic raw datasets")
    parser.add_argument('--clean-only', action='store_true', help="Only run cleaning and validation")
    parser.add_argument('--no-db', action='store_true', help="Skip database table loading")
    args = parser.parse_args()

    if args.clean_only:
        run_pipeline(generate=False, clean=True, validate=True, transform=False, load_db=False)
    elif args.all or args.generate:
        run_pipeline(generate=True, clean=True, validate=True, transform=True, load_db=not args.no_db)
    else:
        run_pipeline(generate=False, clean=True, validate=True, transform=True, load_db=not args.no_db)
