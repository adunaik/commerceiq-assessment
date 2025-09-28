import pandas as pd
import json
import os

def load_data():
    # Get base directory (parent of scripts_new)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Input file paths
    catalog_path = os.path.join(base_dir, "internal_catalog_dump.csv")
    inventory_path = os.path.join(base_dir, "inventory_movements.csv")
    performance_path = os.path.join(base_dir, "performance_metrics.csv")
    competitor_path = os.path.join(base_dir, "competitor_intelligence.json")
    marketplace_path = os.path.join(base_dir, "marketplace_snapshot.json")

    # Load CSV files
    catalog = pd.read_csv(catalog_path)
    inventory = pd.read_csv(inventory_path)
    performance = pd.read_csv(performance_path)

    # Load JSON files
    with open(competitor_path) as f:
        competitor = pd.json_normalize(json.load(f))

    with open(marketplace_path) as f:
        marketplace = pd.json_normalize(json.load(f))

    return catalog, inventory, performance, competitor, marketplace

if __name__ == "__main__":
    dfs = load_data()
    for name, df in zip(
        ["catalog", "inventory", "performance", "competitor", "marketplace"], dfs
    ):
        print(f"\n{name.upper()} SAMPLE:\n", df.head())
