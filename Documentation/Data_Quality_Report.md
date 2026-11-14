# Data quality and limitations

## Supplied terrain

The two primary HGT files are 25,934,402 bytes each (3601×3601 signed 16-bit samples). The processor validates dimensions, mosaics adjacent tiles with the shared column handled once, clips processing to 77.5–78.6°E and 17.1–17.8°N, derives slope, and reports coverage, elevation range, valid fraction, and sample resolution. The full mosaic covers 77–79°E and 17–18°N. Raw inputs remain untouched. The stored grid is EPSG:4326; slope uses a local metres-per-degree approximation rather than a reprojected EPSG:32643 raster. Independent elevation cross-validation is outstanding.

## Derived susceptibility and candidate sites

The coarse screening score combines relative elevation rank (55%) and inverse slope (45%). Candidate screening cells require a low terrain score and slope no greater than 8°. Both are uncalibrated heuristics: no rainfall, drainage, land cover, observed water, accessibility, or field inspection is included. Candidate cells are low-confidence investigation locations, never confirmed safe zones.

## Roads and routing

Roads are intended to come from a cached OpenStreetMap extract. OSM may be incomplete or stale. Turn restrictions and conditional access are not fully modeled. Missing hazard values add a configurable cost and remain visible in route explanations. Public Overpass returned truncated responses and HTTP 504s during initial acquisition; no road extract is currently cached, so route calculation is unavailable until a fetch succeeds. No current observed flood or verified closure layer is configured, so this prototype cannot detect real flooded roads.
