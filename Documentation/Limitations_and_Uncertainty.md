# Limitations and uncertainty

## Evidence available now

- The only supplied environmental data are two HGT elevation tiles. Their grid and coverage were checked, but the source/provider and acquisition date are unknown.
- The derived terrain score is a relative heuristic from elevation rank and slope. It is not a probability, flood forecast, or observation.
- There is no observed flood extent, rainfall, satellite event imagery, drainage network, official closure feed, or validated infrastructure hazard layer.
- OpenStreetMap retrieval has not succeeded, so no real road graph is cached and real route recommendations cannot currently be generated.

## Interpretation limits

- High elevation and low terrain score do not establish that a location is safe.
- A low score does not establish that a road is dry, passable, or accessible.
- Candidate terrain cells are low-confidence places to investigate. They have no field verification or access assessment.
- Missing hazard information receives a nonzero routing penalty and is reported as unknown. Unknown road conditions must not be interpreted as safe.
- The configured observed-flood and closure GeoJSON inputs are supported by the engine but currently unset. Confirmed closure polygons are excluded from routes; observed flood polygons receive a large cost.
- A route recommendation, once a road graph is available, is the lowest configured cost among the generated graph paths. It is not a guarantee of safety or a substitute for emergency authorities.

## Validation needed before operational use

Acquire authoritative event flood observations and road closures; validate the DEM and CRS; add drainage, rainfall, and access evidence; verify road restrictions and route coverage; compare candidate sites with field evidence; and evaluate route rankings against historical flood events and emergency response records.
