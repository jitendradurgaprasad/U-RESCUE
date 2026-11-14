"""Read user-supplied GeoJSON hazard polygons and test road sample points."""
import json
from pathlib import Path

def load_polygons(path):
    if not path:
        return []
    path=Path(path)
    if not path.is_absolute():
        path=Path(__file__).resolve().parents[1]/path
    if not path.exists():
        return []
    data=json.loads(path.read_text(encoding="utf-8"))
    features=data.get("features",[]) if data.get("type")=="FeatureCollection" else [data]
    return [f.get("geometry",f) for f in features if f.get("geometry",f).get("type") in ("Polygon","MultiPolygon")]

def _ring_contains(point, ring):
    x,y=point; inside=False
    for (x1,y1),(x2,y2) in zip(ring,ring[1:]):
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1+1e-30)+x1:
            inside=not inside
    return inside

def contains(point, geometries):
    for geom in geometries:
        polygons=geom["coordinates"] if geom["type"]=="MultiPolygon" else [geom["coordinates"]]
        for polygon in polygons:
            if polygon and _ring_contains(point,polygon[0]) and not any(_ring_contains(point,hole) for hole in polygon[1:]):
                return True
    return False
