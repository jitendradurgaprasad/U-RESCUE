# Data sources and collection status

- **Elevation:** local `n17e077.hgt` and `n17e078.hgt` files supplied in the Desktop project's dataset folder. Each is 25,934,402 bytes, consistent with 3601×3601 signed 16-bit HGT. Their provenance and acquisition date are not embedded; provider attribution remains unverified. Processing reads the files without modifying them.
- **Roads:** intended source is OpenStreetMap via [Overpass API](https://overpass-api.de/api/interpreter), fetched with `python scripts/fetch_roads.py`. The first acquisition attempt failed with truncated JSON and HTTP 504 responses, even after spatial tiling; no roads are claimed as downloaded. OSM is community mapped; verify completeness, access, and closures. ODbL attribution applies.
- **Observed flood extent, current rainfall, hydrology, and verified closures:** not available in the supplied files or configured. No synthetic observations are substituted.
- **Basemap:** MapLibre GL JS renders OpenFreeMap's hosted `liberty` vector style (`https://tiles.openfreemap.org/styles/liberty`). OpenFreeMap's quick start currently shows this public style without an API key. Visible attribution credits OpenStreetMap contributors and OpenFreeMap. Its service is provided as-is and remains subject to the provider's terms; this application no longer requests raster tiles from `tile.openstreetmap.org`.

Terrain susceptibility is derived from relative elevation and slope only. It is not a calibrated flood probability, an observed flood extent, or a road passability label.
