# Implementation status

Last updated: 2026-11-03.

## Implemented

- HGT discovery, dimension validation, adjacent-tile mosaic, slope derivation, and terrain susceptibility output.
- Low-confidence candidate terrain-screening cells (explicitly not verified safe zones).
- Elevation search accepts browser geolocation or a map click and a selected radius, then returns and marks up to two highest spatially separated terrain samples.
- The API requests pedestrian routes to each returned point from the public FOSSGIS Valhalla service using OpenStreetMap data; the UI draws available path lines.
- The current browser screen shows the map, live-location button, radius selector, status and results. Routing requires internet and may fail if the public service or mapped pedestrian network is unavailable.
- Legacy terrain, candidate-area and route endpoints remain in the backend for compatibility.

## Not validated or unavailable

- No observed flood, rainfall, drainage, verified closures, or infrastructure hazards in supplied data.
- The terrain grid is stored in EPSG:4326 and uses approximate local metric spacing; it has not been reprojected to the configured EPSG:32643 analysis CRS.
- No safe-zone layer is confirmed by flood, accessibility, or site evidence.
- Public routing-service availability and OSM pedestrian-network completeness have not been verified for every location in the study area.
- No real flood event validation or model evaluation is possible with current inputs.
