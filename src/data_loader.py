# Import pandas for reading CSV files
import pandas as pd

# Import Path for platform-independent file paths
from pathlib import Path


# Get project root folder (AI Journey)
BASE_DIR = Path(__file__).resolve().parents[1]

# Point to datasets folder
DATA_DIR = BASE_DIR / "datasets"


# Load warehouse KPI fact table
def load_kpi_data():
    return pd.read_csv(DATA_DIR / "warehouse_kpi_data.csv")


# Load employee hierarchy
def load_employee_hierarchy():
    return pd.read_csv(DATA_DIR / "employee_hierarchy.csv")


# Load warehouse metadata
def load_warehouse_master():
    return pd.read_csv(DATA_DIR / "warehouse_master.csv")


# Load KPI benchmark thresholds
def load_benchmarks():
    return pd.read_csv(DATA_DIR / "warehouse_benchmarks.csv")


# Load recommendation rules
def load_recommendation_rules():
    return pd.read_csv(DATA_DIR / "recommendation_rules.csv")


# Load KPI descriptions and metadata
def load_data_dictionary():
    return pd.read_csv(DATA_DIR / "data_dictionary.csv")


# Load sample business questions for testing and demos
def load_demo_questions():
    return pd.read_csv(DATA_DIR / "demo_questions.csv")


# Load every dataset into one dictionary
def load_all_data():
    return {
        "kpi_data": load_kpi_data(),
        "employee_hierarchy": load_employee_hierarchy(),
        "warehouse_master": load_warehouse_master(),
        "benchmarks": load_benchmarks(),
        "recommendation_rules": load_recommendation_rules(),
        "data_dictionary": load_data_dictionary(),
        "demo_questions": load_demo_questions()
    }


# Run only when this file is executed directly
if __name__ == "__main__": 

    # Load all datasets
    data = load_all_data()

    # Print dataset names and dimensions
    for name, df in data.items():
        print(f"{name}: {df.shape}")