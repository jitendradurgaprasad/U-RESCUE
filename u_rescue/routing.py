"""Risk-aware candidate route ranking with explicit unknown-data handling."""
import math
import networkx as nx
import numpy as np

def haversine(a,b):
    lon1,lat1=a; lon2,lat2=b; p=math.pi/180
    x=(lon2-lon1)*p*math.cos((lat1+lat2)*p/2); y=(lat2-lat1)*p
    return 6371000*math.hypot(x,y)

def nearest_node(nodes, point):
    best = min(nodes, key=lambda n:haversine(nodes[n],point))
    return best,haversine(nodes[best],point)

def risk_at(grid, point):
    if grid is None:
        return None
    ix=int(np.argmin(abs(grid["lons"]-point[0])))
    iy=int(np.argmin(abs(grid["lats"]-point[1])))
    value=float(grid["risk"][iy,ix])
    return value if math.isfinite(value) else None

def edge_cost(attrs, grid, weights, observed=None, closures=None):
    length=attrs["length_m"]
    a,b=attrs["geometry"]
    samples=[(a[0]+(b[0]-a[0])*i/4,a[1]+(b[1]-a[1])*i/4) for i in range(5)]
    values=[risk_at(grid,p) for p in samples] if grid else []
    unknown=len(values)<len(samples) or any(v is None for v in values)
    known_values=[v for v in values if v is not None]
    predicted=sum(known_values)/len(known_values) if known_values else None
    flooded=bool(observed and any(observed(p) for p in samples))
    closed=bool(closures and any(closures(p) for p in samples))
    detail={"distance_m":length,"predicted_risk":predicted,"observed_flood":flooded,"closed":closed,"unknown":unknown}
    if closed:
        return math.inf,detail
    if flooded:
        return weights["observed_flood_penalty"],detail
    risk=(predicted or 0)+(weights["unknown_data_penalty"] if unknown else 0)
    return length*(weights["distance_weight"]+weights["predicted_risk_weight"]*risk),detail

def route_candidates(graph,nodes,start,end,grid,weights,k=5,observed=None,closures=None):
    source,start_gap=nearest_node(nodes,start); target,end_gap=nearest_node(nodes,end)
    if start_gap>weights["snap_limit_m"] or end_gap>weights["snap_limit_m"]:
        raise ValueError("Start or destination is too far from a mapped road")
    simple=nx.DiGraph()
    for u,v,_,attrs in graph.edges(keys=True,data=True):
        cost,detail=edge_cost(attrs,grid,weights,observed,closures)
        if math.isfinite(cost) and (not simple.has_edge(u,v) or cost<simple[u][v]["weight"]):
            simple.add_edge(u,v,weight=cost,detail=detail,attrs=attrs)
    try:
        paths=nx.shortest_simple_paths(simple,source,target,weight="weight")
        results=[]
        for path in paths:
            segments=[simple[u][v] for u,v in zip(path,path[1:])]
            details=[s["detail"] for s in segments]
            distance=sum(d["distance_m"] for d in details)
            known=[d["predicted_risk"] for d in details if d["predicted_risk"] is not None]
            results.append({"cost":sum(s["weight"] for s in segments),"distance_m":distance,
                "predicted_risk_mean":sum(known)/len(known) if known else None,
                "observed_flood_segments":sum(d["observed_flood"] for d in details),
                "unknown_segments":sum(d["unknown"] for d in details),"segment_count":len(segments),
                "coordinates":[nodes[n] for n in path],
                "segments":[{"coordinates":s["attrs"]["geometry"],"name":s["attrs"].get("name", ""),
                    "highway":s["attrs"].get("highway", "road"),**s["detail"]} for s in segments]})
            if len(results)>=k:
                break
        return results
    except (nx.NetworkXNoPath,nx.NodeNotFound):
        return []

def turn_directions(segments):
    """Build concise spoken maneuvers from routed edge geometry."""
    if not segments:
        return []
    def bearing(coords):
        (lon1,lat1),(lon2,lat2)=coords
        p1,p2=math.radians(lat1),math.radians(lat2)
        dl=math.radians(lon2-lon1)
        y=math.sin(dl)*math.cos(p2)
        x=math.cos(p1)*math.sin(p2)-math.sin(p1)*math.cos(p2)*math.cos(dl)
        return (math.degrees(math.atan2(y,x))+360)%360
    def road_name(segment):
        return segment.get("name") or "the unnamed road"
    headings=["north","northeast","east","southeast","south","southwest","west","northwest"]
    initial=bearing(segments[0]["coordinates"])
    instructions=[f"Start by heading {headings[round(initial/45)%8]} on {road_name(segments[0])}."]
    walked=0.0
    last_name=road_name(segments[0])
    for i in range(1,len(segments)):
        previous,current=segments[i-1],segments[i]
        walked+=previous.get("distance_m",0)
        delta=(bearing(current["coordinates"])-bearing(previous["coordinates"])+540)%360-180
        name=road_name(current)
        changed=name!=last_name and name!="the unnamed road"
        if abs(delta)>=35:
            turn="make a U-turn" if abs(delta)>=150 else ("turn right" if delta>0 else "turn left")
            instructions.append(f"In {max(10,round(walked/10)*10)} meters, {turn} onto {name}.")
            last_name=name
            walked=0
        elif changed:
            instructions.append(f"In {max(10,round(walked/10)*10)} meters, continue onto {name}.")
            last_name=name
            walked=0
    instructions.append("You are approaching your destination.")
    return instructions
