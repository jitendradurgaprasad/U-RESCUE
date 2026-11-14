"""Read HGT tiles and derive a coarse relative terrain susceptibility surface."""
import json
from pathlib import Path
import numpy as np

def read_hgt(path):
    a = np.fromfile(path, dtype=">i2")
    side = int(np.sqrt(a.size))
    if side * side != a.size or side not in (1201, 3601):
        raise ValueError(f"Unexpected HGT dimensions: {path} ({a.size} samples)")
    return a.reshape(side, side).astype(np.float32)

def process(data_dir, output_dir, stride=12, study_bbox=None):
    data_dir, output_dir = Path(data_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths=sorted((p for p in data_dir.rglob("*.hgt") if p.stem.lower() in {"n17e077","n17e078"}),
        key=lambda p:(p.parent.name.lower()=="raw" and p.parent.parent.name.lower()=="dem",str(p)))
    tiles={}
    selected_paths={}
    for path in paths:
        key=path.stem.lower()
        if key not in tiles or (path.parent.name.lower()=="raw" and path.parent.parent.name.lower()=="dem"):
            tiles[key]=read_hgt(path)
            selected_paths[key]=str(path)
    if not tiles:
        raise FileNotFoundError("No n17e077.hgt or n17e078.hgt found under configured data directory")
    if "n17e077" in tiles and "n17e078" in tiles:
        a, b = tiles["n17e077"], tiles["n17e078"]
        if a.shape != b.shape:
            raise ValueError("HGT tiles have incompatible dimensions")
        dem, west = np.concatenate([a[:, :-1], b], axis=1), 77.0
    elif "n17e077" in tiles:
        dem, west = tiles["n17e077"], 77.0
    else:
        dem, west = tiles["n17e078"], 78.0
    rows, cols = dem.shape
    tile_cols = next(iter(tiles.values())).shape[1]
    north, dlat, dlon = 18.0, 1/(rows-1), 1/(tile_cols-1)
    full_bounds=[west,17.0,west+(cols-1)*dlon,18.0]
    if study_bbox:
        min_lon,min_lat,max_lon,max_lat=study_bbox
        c0=max(0,int(round((min_lon-west)/dlon))); c1=min(cols,int(round((max_lon-west)/dlon))+1)
        r0=max(0,int(round((north-max_lat)/dlat))); r1=min(rows,int(round((north-min_lat)/dlat))+1)
        if c1<=c0 or r1<=r0:
            raise ValueError("Configured study boundary does not intersect the available HGT tiles")
        dem=dem[r0:r1,c0:c1]
        west=west+c0*dlon; north=north-r0*dlat
        rows,cols=dem.shape
    valid = (dem > -1000) & (dem < 9000)
    dem[~valid] = np.nan
    dy, dx = 111320*dlat, 111320*dlon*np.cos(np.deg2rad(17.5))
    gy, gx = np.gradient(np.nan_to_num(dem, nan=np.nanmedian(dem)), dy, dx)
    slope = np.degrees(np.arctan(np.hypot(gx, gy))).astype(np.float32)
    sample, sl = dem[::stride, ::stride], slope[::stride, ::stride]
    elev_ok = np.isfinite(sample)
    elev_rank = np.zeros(sample.shape, np.float32)
    vals = sample[elev_ok]
    unique, inverse, counts = np.unique(vals, return_inverse=True, return_counts=True)
    if len(unique)>1:
        rank_by_value=(np.cumsum(counts)-counts/2)/len(vals)
        elev_rank[elev_ok]=rank_by_value[inverse]
    elif len(vals):
        elev_rank[elev_ok]=.5
    risk = np.where(elev_ok, .55*(1-elev_rank) + .45*np.clip(1-sl/25, 0, 1), np.nan).astype(np.float32)
    lons = west + np.arange(sample.shape[1])*stride*dlon
    lats = north - np.arange(sample.shape[0])*stride*dlat
    np.savez_compressed(output_dir/"terrain_risk_grid.npz", risk=risk, elevation=sample, slope=sl, lons=lons, lats=lats, valid=elev_ok)
    metadata = {"source_tiles": list(tiles), "source_files":selected_paths, "dimensions_processed": list(dem.shape), "full_tile_bounds":full_bounds,"crs":"EPSG:4326",
      "bounds":[west,north-(rows-1)*dlat,west+(cols-1)*dlon,north], "valid_fraction":float(valid.mean()),
      "elevation_min_m":float(np.nanmin(dem)), "elevation_max_m":float(np.nanmax(dem)),
      "elevation_median_m":float(np.nanmedian(dem)), "stride_samples":stride,
      "resolution_approx_m":round(111320*dlat*stride),
      "risk_method":"relative elevation rank (55%) + inverse slope (45%); terrain-only heuristic, not observed flooding or calibrated probability",
      "nodata_sample_fraction":float((~elev_ok).mean())}
    (output_dir/"terrain_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata
