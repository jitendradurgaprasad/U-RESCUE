from pathlib import Path
from contextlib import asynccontextmanager
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from u_rescue.settings import settings
from u_rescue.terrain import process
from u_rescue.walking_router import walking_route
from u_rescue.hazards import load_polygons,contains

S=settings()
_grid=_graph=_nodes=_road_data=None
_flood_polygons=[]
_closure_polygons=[]

@asynccontextmanager
async def lifespan(application):
    try:
        initialize()
    except Exception as exc:
        application.state.startup_error=str(exc)
    yield

app=FastAPI(title="U RESCUE",description="Flood risk decision support; routes are not guaranteed safe",lifespan=lifespan)

def initialize():
    global _grid,_graph,_nodes,_road_data,_flood_polygons,_closure_polygons
    out=S["output_dir"]
    if not (out/"terrain_risk_grid.npz").exists():
        process(S["data_dir"],out,study_bbox=S["study_area"]["bbox"])
    z=np.load(out/"terrain_risk_grid.npz")
    _grid={key:z[key] for key in z.files}
    # Walking routes use the public OSM-based Valhalla service on demand. Do not
    # load a huge regional road graph into laptop memory at startup.
    _flood_polygons=load_polygons(S["hazards"].get("observed_flood_layer"))
    _closure_polygons=load_polygons(S["hazards"].get("known_closures_layer"))

@app.get("/api/status")
def status():
    return {"ready":_grid is not None,"error":getattr(app.state,"startup_error",None),
        "road_nodes":len(_nodes) if _nodes else 0,"road_edges":_graph.number_of_edges() if _graph else 0,
        "terrain":_grid is not None,"observed_flood_data":bool(_flood_polygons),
        "closure_data":bool(_closure_polygons),
        "walking_router":"Public OpenStreetMap-based Valhalla service; internet required",
        "warning":"No observed flood extent or verified closure feed configured. Terrain is a relative susceptibility proxy."}

@app.get("/api/layers")
def layers():
    if _grid is None:
        raise HTTPException(503,"Terrain layer unavailable")
    features=[]; risk=_grid["risk"]; elev=_grid["elevation"]; slope=_grid["slope"]
    for iy in range(0,risk.shape[0],3):
        for ix in range(0,risk.shape[1],3):
            value=float(risk[iy,ix])
            if not np.isfinite(value):
                continue
            lon,lat=float(_grid["lons"][ix]),float(_grid["lats"][iy]); size=.012
            features.append({"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[lon,lat],[lon+size,lat],[lon+size,lat-size],[lon,lat-size],[lon,lat]]]},
                "properties":{"risk":value,"elevation_m":float(elev[iy,ix]),"slope_deg":float(slope[iy,ix]),"kind":"terrain_susceptibility_proxy"}})
    return {"type":"FeatureCollection","features":features}

@app.get("/api/safe-zones")
def safe_zones():
    """Return terrain-screening candidates; these are not verified safe zones."""
    if _grid is None:
        raise HTTPException(503,"Terrain layer unavailable")
    risk,elev,slope=_grid["risk"],_grid["elevation"],_grid["slope"]
    valid=np.isfinite(risk)
    candidates=valid & (risk<=float(np.nanquantile(risk[valid],.25))) & (slope<=8)
    features=[]; size=36/3600
    for iy,ix in zip(*np.where(candidates)):
        lon,lat=float(_grid["lons"][ix]),float(_grid["lats"][iy])
        features.append({"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[lon,lat],[lon+size,lat],[lon+size,lat-size],[lon,lat-size],[lon,lat]]]},
          "properties":{"kind":"candidate_terrain_screening_cell","elevation_m":float(elev[iy,ix]),"slope_deg":float(slope[iy,ix]),"terrain_score":float(risk[iy,ix]),"confidence":"low","limitations":"No flood observations, accessibility, drainage, land-use or site inspection evidence. Not confirmed safe."}})
    return {"type":"FeatureCollection","features":features}

@app.get("/api/elevated-areas")
def elevated_areas(lon:float=Query(...,ge=-180,le=180),lat:float=Query(...,ge=-90,le=90),
                   radius_km:float=Query(...,gt=0,le=100)):
    """Return the two highest distinct sampled elevation cells within a radius."""
    if _grid is None:
        raise HTTPException(503,"Terrain layer unavailable")
    elev=np.asarray(_grid["elevation"]); lons=np.asarray(_grid["lons"]); lats=np.asarray(_grid["lats"])
    valid=np.isfinite(elev)
    latr=np.deg2rad(float(lat)); lonr=np.deg2rad(float(lon))
    lat_grid=np.deg2rad(lats)[:,None]; lon_grid=np.deg2rad(lons)[None,:]
    dlat=lat_grid-latr; dlon=lon_grid-lonr
    a=np.sin(dlat/2)**2+np.cos(latr)*np.cos(lat_grid)*np.sin(dlon/2)**2
    distance_m=6371000*2*np.arctan2(np.sqrt(a),np.sqrt(np.maximum(0,1-a)))
    inside=valid & (distance_m<=radius_km*1000)
    cells=sorted(zip(*np.where(inside)),key=lambda ij:float(elev[ij]),reverse=True)
    selected=[]
    # Grid samples represent broad terrain (~371 m spacing). Suppress adjacent
    # samples so the two markers identify separate nearby areas, not one ridge.
    for iy,ix in cells:
        point=(float(lons[ix]),float(lats[iy]))
        if any(float(np.hypot((point[0]-p[0])*111320*np.cos(latr),(point[1]-p[1])*111320))<500 for p in (s[0] for s in selected)):
            continue
        selected.append((point,float(elev[iy,ix]),float(distance_m[iy,ix])))
        if len(selected)==2:break
    areas=[]
    for i,(point,z,dist) in enumerate(selected):
        area={"rank":i+1,"lon":point[0],"lat":point[1],"elevation_m":z,"distance_m":dist,"route":None}
        try:
            route=walking_route((lon,lat),point)
            area["route"]={**route,"segment_count":None,"unknown_segments":None}
        except RuntimeError as exc:
            area["route_error"]=str(exc)
        areas.append(area)
    return {"origin":{"lon":lon,"lat":lat},"radius_km":radius_km,
        "sample_spacing_m":371,"count":len(selected),"areas":areas,
        "road_network_available":True,"routing_source":"OpenStreetMap via FOSSGIS Valhalla public demo",
        "note":"Highest sampled terrain points in the selected radius. Approximate terrain screening only; not verified safe or accessible."}

@app.get("/api/hazards")
def hazards():
    features=[]
    for label,geometries in (("observed_flood",_flood_polygons),("known_closure",_closure_polygons)):
        features.extend({"type":"Feature","geometry":geometry,"properties":{"kind":label}} for geometry in geometries)
    return {"type":"FeatureCollection","features":features}

@app.get("/api/roads")
def roads():
    if _road_data is None:
        raise HTTPException(503,"Road graph unavailable")
    coords={e["id"]:(e["lon"],e["lat"]) for e in _road_data["elements"] if e["type"]=="node"}
    features=[]
    for e in _road_data["elements"]:
        if e["type"]!="way" or "highway" not in e.get("tags",{}):
            continue
        line=[coords[n] for n in e["nodes"] if n in coords]
        if len(line)>1:
            features.append({"type":"Feature","geometry":{"type":"LineString","coordinates":line},"properties":{"highway":e["tags"].get("highway"),"name":e["tags"].get("name","")}})
    return {"type":"FeatureCollection","features":features}

@app.post("/api/routes")
def routes(req:dict):
    try:
        start=tuple(map(float,req["start"])); destination=tuple(map(float,req["destination"]))
        route=walking_route(start,destination)
        return {"recommended":route,"alternatives":[],"explanation":"Walking route based on OpenStreetMap data.",
            "warning":"Route reflects mapped pedestrian access only; it does not establish flood safety or current passability."}
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(502,str(exc))
    except (KeyError,ValueError,TypeError) as exc:
        raise HTTPException(400,str(exc))

@app.get("/",response_class=HTMLResponse)
def home():
    return (Path(__file__).parent/"web"/"index.html").read_text(encoding="utf-8")
