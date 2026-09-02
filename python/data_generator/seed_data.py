"""
Seed Data Script for Global Supply Chain Digital Twin Platform.
Generates local CSV data files in data/bronze/ and attempts DB/MinIO seeding.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

from python.data_generator.generate_mock_data import generate_dataset
from python.utils.logger import get_logger

logger = get_logger("SeedData")

def seed():
    bronze_dir = BASE_DIR / "data" / "bronze"
    bronze_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Generating synthetic datasets for seeding...")
    dataset = generate_dataset(num_orders=500, num_iot_events=1500)

    for name, df in dataset.items():
        csv_path = bronze_dir / f"raw_{name}.csv"
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved {len(df)} records to {csv_path}")

    logger.info("Data seeding completed successfully!")

if __name__ == "__main__":
    seed()
