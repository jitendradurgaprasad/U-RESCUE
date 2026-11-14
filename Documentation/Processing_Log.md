# Processing log

- Dataset inventory found two primary adjacent HGT tiles in the supplied Desktop project's `Datasets/01_Terrain/Raw/DEM/Raw` folder. A separate DEM directory contained one HGT plus `.num` and `.swb` auxiliaries. Optical, radar, climate, hydrology, road, and output folders were empty.
- Validated both primary HGT dimensions (3601×3601), mosaicked to 3601×7201, cropped to the configured 77.5–78.6°E / 17.1–17.8°N study area, derived slope and a coarse terrain-only score. Outputs are in local `data/processed/terrain_risk_grid.npz` and `terrain_metadata.json`.
- Implemented OSM Overpass retrieval/cache and graph conversion. Acquisition attempts on 2026-10-14 failed: the public service returned truncated JSON and HTTP 504 responses, including after retrying smaller bounding-box tiles. No road data is claimed as collected. App startup does not block on the network; run the fetch script when Overpass is available.
- No observed-flood, rainfall, hydrology, or closure layer was collected.
