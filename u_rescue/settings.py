import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def settings():
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    cfg["data_dir"] = Path(os.getenv("URESCUE_DATA_DIR", str(ROOT / "data/source")))
    cfg["output_dir"] = Path(os.getenv("URESCUE_OUTPUT_DIR", str(ROOT / "data/processed")))
    cfg["osm_cache"] = Path(os.getenv("URESCUE_OSM_CACHE", str(ROOT / "data/osm_roads.json")))
    return cfg
