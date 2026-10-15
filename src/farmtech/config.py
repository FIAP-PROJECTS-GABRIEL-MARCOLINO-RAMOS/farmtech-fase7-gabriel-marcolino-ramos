from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path(os.getenv('FARMTECH_DB', str(ROOT / 'runtime/farmtech.db')))
SEED = 565717
