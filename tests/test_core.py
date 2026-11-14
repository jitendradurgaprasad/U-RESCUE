import networkx as nx
import numpy as np
from u_rescue.routing import edge_cost,route_candidates,turn_directions
from u_rescue.hazards import contains
from u_rescue.roads import graph_from_osm

def test_missing_hazard_data_has_nonzero_penalty():
    edge={"geometry":[(0,0),(.01,0)],"length_m":1000}
    cost,detail=edge_cost(edge,None,{"distance_weight":1,"predicted_risk_weight":3,"unknown_data_penalty":.25,"observed_flood_penalty":1_000_000})
    assert cost>1000 and detail["unknown"]

def test_partial_hazard_coverage_is_still_marked_unknown():
    edge={"geometry":[(0,0),(.01,0)],"length_m":1000}
    grid={"lons":np.array([0,.01]),"lats":np.array([0]),"risk":np.array([[.1,np.nan]])}
    cost,detail=edge_cost(edge,grid,{"distance_weight":1,"predicted_risk_weight":3,"unknown_data_penalty":.25,"observed_flood_penalty":1_000_000})
    assert detail["unknown"] and detail["predicted_risk"] is not None and cost>1000

def test_observed_flood_penalty_dominates():
    edge={"geometry":[(0,0),(.01,0)],"length_m":1000}
    cost,detail=edge_cost(edge,None,{"distance_weight":1,"predicted_risk_weight":3,"unknown_data_penalty":.25,"observed_flood_penalty":1_000_000},observed=lambda _:True)
    assert cost==1_000_000 and detail["observed_flood"]

def test_confirmed_closure_excludes_edge():
    edge={"geometry":[(0,0),(.01,0)],"length_m":1000}
    cost,detail=edge_cost(edge,None,{"distance_weight":1,"predicted_risk_weight":3,"unknown_data_penalty":.25,"observed_flood_penalty":1_000_000},closures=lambda _:True)
    assert cost==float("inf") and detail["closed"]

def test_polygon_hazard_intersection():
    polygon={"type":"Polygon","coordinates":[[[0,0],[1,0],[1,1],[0,1],[0,0]]]}
    assert contains((.5,.5),[polygon])
    assert not contains((2,2),[polygon])

def test_osm_oneway_and_private_access():
    data={"elements":[
      {"type":"node","id":1,"lon":78.0,"lat":17.0},
      {"type":"node","id":2,"lon":78.01,"lat":17.0},
      {"type":"way","id":10,"nodes":[1,2],"tags":{"highway":"primary","oneway":"-1"}},
      {"type":"way","id":11,"nodes":[1,2],"tags":{"highway":"residential","access":"private"}}]}
    graph,nodes=graph_from_osm(data)
    assert graph.has_edge(2,1)
    assert not graph.has_edge(1,2)
    assert graph.number_of_edges()==1

def test_spoken_turn_instructions_from_route_edges():
    segments=[
      {"coordinates":[(78.0,17.0),(78.01,17.0)],"distance_m":1000,"name":"First Road"},
      {"coordinates":[(78.01,17.0),(78.01,16.99)],"distance_m":700,"name":"Second Road"}]
    steps=turn_directions(segments)
    assert steps[0].startswith("Start by heading east on First Road")
    assert any("turn right" in step and "Second Road" in step for step in steps)
    assert steps[-1].startswith("You are approaching")

def test_risk_route_can_beat_shortest_route():
    graph=nx.MultiDiGraph(); nodes={1:(0,0),2:(.01,0),3:(0,.01),4:(.01,.01)}
    for u,v,length in [(1,2,1000),(2,4,1000),(1,3,1200),(3,4,1200)]:
        graph.add_edge(u,v,length_m=length,geometry=[nodes[u],nodes[v]])
    grid={"lons":np.array([0,.01]),"lats":np.array([.01,0]),"risk":np.array([[.1,.1],[.9,.9]])}
    weights={"distance_weight":1,"predicted_risk_weight":4,"unknown_data_penalty":.25,"observed_flood_penalty":1_000_000,"snap_limit_m":5000}
    result=route_candidates(graph,nodes,(0,0),(.01,.01),grid,weights,2)
    assert len(result)==2
    assert result[0]["distance_m"]>result[1]["distance_m"]
    assert result[0]["predicted_risk_mean"]<result[1]["predicted_risk_mean"]
