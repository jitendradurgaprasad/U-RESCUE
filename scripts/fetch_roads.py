import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from u_rescue.settings import settings
from u_rescue.roads import load_roads,graph_from_osm

if __name__ == "__main__":
    config=settings()
    data=load_roads(config["osm_cache"],config["study_area"]["bbox"])
    graph,nodes=graph_from_osm(data)
    print(f"Cached {len(nodes)} nodes and {graph.number_of_edges()} directed road edges")
