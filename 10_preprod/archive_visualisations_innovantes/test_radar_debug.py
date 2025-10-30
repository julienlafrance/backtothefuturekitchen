#!/usr/bin/env python3
"""Debug radar chart preparation."""

import sys
from pathlib import Path
import pandas as pd

# Ajouter le chemin vers le module
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from mangetamain_analytics.pages import __file__ as pages_init
pages_dir = Path(pages_init).parent
sys.path.insert(0, str(pages_dir.parent))

# Importer la fonction à tester
import importlib.util
spec = importlib.util.spec_from_file_location("innovative_page",
    pages_dir / "5_🚀_Visualisations_Innovantes.py")
module = importlib.util.module_from_spec(spec)

print("Loading page module...")
try:
    spec.loader.exec_module(module)
    print("✅ Module loaded")
except Exception as e:
    print(f"❌ Error loading module: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nLoading data...")
try:
    df = module.load_recipes_with_ratings()
    print(f"✅ Data loaded: {len(df)} rows")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Season values: {df['season'].value_counts() if 'season' in df.columns else 'NO SEASON COLUMN'}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nPreparing seasonal profiles...")
try:
    profiles = module.prepare_seasonal_profiles(df)
    print(f"✅ Profiles prepared: {len(profiles)} rows")

    # Afficher toutes les colonnes
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(f"\n{profiles}")

    if len(profiles) == 0:
        print("\n⚠️  EMPTY DATAFRAME RETURNED")
        print("   Checking season column...")
        if "season" not in df.columns:
            print("   ❌ NO SEASON COLUMN")
        else:
            print(f"   Season column exists with {df['season'].notna().sum()} non-null values")
            print(f"   Unique seasons: {df['season'].unique()}")
except Exception as e:
    print(f"❌ Error preparing profiles: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
