import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from u_rescue.settings import settings
from u_rescue.terrain import process

if __name__ == "__main__":
    config=settings()
    print(process(config["data_dir"],config["output_dir"],study_bbox=config["study_area"]["bbox"]))
