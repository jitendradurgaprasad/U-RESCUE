# U RESCUE

A terrain-screening prototype for exploring the highest sampled elevation areas around a chosen location in the configured Hyderabad and Sangareddy study area. It is not a flood-safety or navigation service.

## Data available

The supplied external dataset contains two adjacent HGT tiles. It did not include observed flood extent, satellite imagery, rainfall, hydrology, road closures, or validated safe zones. OpenStreetMap roads can be retrieved through Overpass and cached; public Overpass returned incomplete responses during initial acquisition. See `Documentation/` for sources, inventory, quality limits, and implementation status.

## Setup (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:URESCUE_DATA_DIR = "C:\path\to\DIGITALTWIN_U_RESCUE\U_RESCUE\Datasets"
python scripts/process_terrain.py
uvicorn app:app --reload
```

On Windows, run `install_project.bat` once, then `start_project.bat`. Open `http://127.0.0.1:8000`. Use **Use my live location** (after granting browser location permission) or click a point on the map. Choose a search range; the map marks up to two highest distinct elevation samples found within that radius. The data are sampled at approximately 371 m spacing, so the markers are broad terrain references and are not verified shelters, accessible places, or safe destinations. The page uses MapLibre with OpenFreeMap vector tiles and requires internet access for the basemap; no map API key is needed.

`/api/elevated-areas?lon=<longitude>&lat=<latitude>&radius_km=<kilometres>` returns up to two highest distinct sampled terrain points inside the chosen radius and requests pedestrian routes to them from the public FOSSGIS Valhalla demo server using OpenStreetMap data. The routing service needs an internet connection and applies a fair-use policy; routing may be unavailable if its service is down or the map has no connected pedestrian path.

## Cost model

Elevation ranking uses the supplied terrain samples only. It does not predict flood depth or flow, and the search does not assess water, roads, accessibility, land ownership, buildings, or emergency-service advice. Use current local authority information during an emergency.

For tests, install `requirements-dev.txt` and run `python -m pytest -q`. Processing can be repeated with `python scripts/process_terrain.py`; source HGTs are not modified.
