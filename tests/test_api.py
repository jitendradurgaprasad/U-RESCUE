import networkx as nx
from fastapi.testclient import TestClient
import app as application

def test_status_reports_missing_road_cache():
    with TestClient(application.app) as client:
        page=client.get("/")
        assert page.status_code==200 and "U RESCUE" in page.text
        status=client.get("/api/status").json()
        assert status["terrain"]
        assert not status["ready"]
        assert status["road_message"]
        assert client.get("/api/hazards").json()["features"]==[]
        assert client.get("/api/safe-zones").json()["type"]=="FeatureCollection"
        response=client.post("/api/routes",json={"start":[78.4,17.4],"destination":[78.1,17.6]})
        assert response.status_code==503

def test_route_endpoint_returns_comparison(monkeypatch):
    graph=nx.MultiDiGraph()
    nodes={1:(78.1,17.4),2:(78.11,17.4)}
    graph.add_edge(1,2,length_m=1000,geometry=[nodes[1],nodes[2]])
    monkeypatch.setattr(application,"_graph",graph)
    monkeypatch.setattr(application,"_nodes",nodes)
    monkeypatch.setattr(application,"_grid",None)
    with TestClient(application.app) as client:
        response=client.post("/api/routes",json={"start":[78.1,17.4],"destination":[78.11,17.4],"alternatives":2})
        assert response.status_code==200
        body=response.json()
        assert body["recommended"]["distance_m"]==1000
        assert body["shortest_route_comparison"]["distance_m"]==1000
        assert body["recommended"]["directions"][0].startswith("Start by heading")
        assert "warning" in body
