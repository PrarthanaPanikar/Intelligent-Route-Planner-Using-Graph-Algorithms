"""
==============================================================================
GRAPH LOADER: Load Road Network and Define Cost Functions
==============================================================================
This module loads the CSV road network and creates a graph representation.
It also provides various cost functions for different optimization objectives.

Cost Functions:
- time_cost: Travel time (considering speed and traffic)
- distance_cost: Total distance traveled
- money_cost: Toll charges
- eco_cost: Environmental impact proxy

Created for: Intelligent Route Planner - DSA Project
==============================================================================
"""

import csv
import math


class RoadNetwork:
    """
    Graph representation of the road network using Adjacency List.
    
    Data Structure: Adjacency List
    ==============================
    nodes: dict[node_id -> set of neighbors]
    edges: dict[(u, v) -> edge attributes]
    
    Why Adjacency List?
    - Space efficient for sparse graphs (typical road networks)
    - Fast neighbor lookup O(1) average
    - Easy to iterate over edges
    - Common in routing engines (Google Maps, OSM Routing)
    """
    
    def __init__(self):
        self.nodes = {}  # node_id -> set of neighbor node IDs
        self.edges = {}  # (u, v) -> {attributes}
        self.node_coords = {}  # node_id -> (lat, lon)
    
    def add_node(self, node_id, lat, lon):
        """Add a node to the graph."""
        if node_id not in self.nodes:
            self.nodes[node_id] = set()
        self.node_coords[node_id] = (lat, lon)
    
    def add_edge(self, u, v, distance_m, speed_kph, toll, one_way, road_class):
        """
        Add a directed edge (u -> v) with attributes.
        
        Parameters:
        -----------
        u, v: Node IDs
        distance_m: Distance in meters
        speed_kph: Average speed in km/h
        toll: Toll cost (0 or 1)
        one_way: One-way flag (0 or 1)
        road_class: Road type (residential, primary, secondary, link)
        """
        # Add nodes if not present (shouldn't happen if data is clean)
        if u not in self.nodes:
            self.nodes[u] = set()
        if v not in self.nodes:
            self.nodes[v] = set()
        
        # Add edge
        self.nodes[u].add(v)
        
        # Calculate base travel time (in seconds)
        base_sec = distance_m / (speed_kph * 1000 / 3600)
        
        # Store edge with attributes
        self.edges[(u, v)] = {
            "distance_m": distance_m,
            "speed_kph": speed_kph,
            "toll": toll,
            "one_way": one_way,
            "road_class": road_class,
            "base_sec": base_sec,
            "traffic_factor": 1.0,  # Default: no traffic
            "lat_u": None,  # Will be filled during load
            "lon_u": None,
            "lat_v": None,
            "lon_v": None,
        }
    
    def get_neighbors(self, node):
        """Get all neighboring nodes."""
        return self.nodes.get(node, set())
    
    def get_edge(self, u, v):
        """Get edge attributes."""
        return self.edges.get((u, v), None)
    
    def all_edges(self):
        """Iterator over all edges."""
        return self.edges.items()
    
    def node_count(self):
        """Total number of nodes."""
        return len(self.nodes)
    
    def edge_count(self):
        """Total number of edges."""
        return len(self.edges)
    
    def copy(self):
        """Create a deep copy of the graph."""
        import copy
        new_graph = RoadNetwork()
        new_graph.nodes = copy.deepcopy(self.nodes)
        new_graph.edges = copy.deepcopy(self.edges)
        new_graph.node_coords = copy.deepcopy(self.node_coords)
        return new_graph


def load_graph(csv_path="data/roads.csv"):
    """
    Load road network from CSV and create graph.
    
    CSV Format:
    u,v,lat_u,lon_u,lat_v,lon_v,distance_m,speed_kph,toll,one_way,road_class
    
    Returns:
    --------
    RoadNetwork: Graph object
    """
    graph = RoadNetwork()
    
    print(f"📂 Loading graph from {csv_path}...")
    
    edge_count = 0
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            u = row["u"]
            v = row["v"]
            lat_u = float(row["lat_u"])
            lon_u = float(row["lon_u"])
            lat_v = float(row["lat_v"])
            lon_v = float(row["lon_v"])
            distance_m = float(row["distance_m"])
            speed_kph = float(row["speed_kph"])
            toll = int(row["toll"])
            one_way = int(row["one_way"])
            road_class = row["road_class"]
            
            # Add nodes
            graph.add_node(u, lat_u, lon_u)
            graph.add_node(v, lat_v, lon_v)
            
            # Add edge with coordinates
            graph.add_edge(u, v, distance_m, speed_kph, toll, one_way, road_class)
            graph.edges[(u, v)]["lat_u"] = lat_u
            graph.edges[(u, v)]["lon_u"] = lon_u
            graph.edges[(u, v)]["lat_v"] = lat_v
            graph.edges[(u, v)]["lon_v"] = lon_v
            
            edge_count += 1
    
    print(f"✅ Loaded {graph.node_count()} nodes and {graph.edge_count()} edges")
    return graph


# ============================================================================
# COST FUNCTIONS: Different optimization objectives
# ============================================================================

def time_cost(edge):
    """
    Travel time cost (in seconds).
    Formula: time = base_time * traffic_factor
    
    This is the PRIMARY objective for most navigation systems (GPS, Google Maps).
    
    Parameters:
    -----------
    edge: Edge attributes dict
    
    Returns:
    --------
    float: Time in seconds
    """
    return edge["base_sec"] * edge.get("traffic_factor", 1.0)


def distance_cost(edge):
    """
    Total distance cost (in meters).
    
    Useful for: Logistics companies tracking delivery distances, 
    fuel consumption estimates.
    
    Parameters:
    -----------
    edge: Edge attributes dict
    
    Returns:
    --------
    float: Distance in meters
    """
    return edge["distance_m"]


def money_cost(edge):
    """
    Monetary cost (toll charges).
    
    Useful for: Budget-conscious travelers, toll optimization.
    
    Parameters:
    -----------
    edge: Edge attributes dict
    
    Returns:
    --------
    int: Toll cost (0 or 1 toll gate)
    """
    return edge["toll"]


def eco_cost(edge):
    """
    Environmental impact proxy cost.
    
    Formula: eco_cost = time_cost * class_factor
    where class_factor favors primary roads (more efficient highways)
    
    Useful for: EV routing, carbon footprint minimization, 
    green delivery initiatives.
    
    Road Class Penalties:
    - primary: 0.9x (efficient highways)
    - secondary: 1.0x (normal roads)
    - residential: 1.1x (slower, more congestion)
    - link: 1.0x (connector roads)
    
    Parameters:
    -----------
    edge: Edge attributes dict
    
    Returns:
    --------
    float: Eco cost (weighted time)
    """
    road_class = edge["road_class"]
    
    # Class-based multipliers
    class_factors = {
        "primary": 0.9,      # Efficient - highways
        "secondary": 1.0,    # Neutral
        "residential": 1.1,  # Congestion penalty
        "link": 1.0          # Standard
    }
    
    factor = class_factors.get(road_class, 1.0)
    return time_cost(edge) * factor


def combined_cost(edge, alpha=1.0, beta=0.2, gamma=5.0):
    """
    Weighted combination of multiple objectives.
    
    Formula: cost = α*time + β*distance + γ*tolls
    
    This models real-world routing preferences:
    - α (time weight): How much user values speed
    - β (distance weight): How much user cares about distance (fuel cost)
    - γ (toll weight): How much user wants to avoid tolls
    
    Example Scenarios:
    - Delivery driver: α=1.0, β=0.5, γ=2.0 (balanced)
    - Executive: α=5.0, β=0.1, γ=10.0 (prefer fast, ignore tolls)
    - Budget traveler: α=1.0, β=0.3, γ=50.0 (avoid tolls at all costs)
    
    Parameters:
    -----------
    edge: Edge attributes dict
    alpha: Time weight (default 1.0)
    beta: Distance weight (default 0.2, scaled to km)
    gamma: Toll weight (default 5.0)
    
    Returns:
    --------
    float: Combined cost
    """
    t = time_cost(edge)
    d = distance_cost(edge) / 1000.0  # Convert to km
    m = money_cost(edge)
    
    return alpha * t + beta * d + gamma * m


if __name__ == "__main__":
    # Test: Load graph and print statistics
    try:
        G = load_graph("data/roads.csv")
        print(f"\n📊 Graph Statistics:")
        print(f"   Nodes: {G.node_count()}")
        print(f"   Edges: {G.edge_count()}")
        print(f"   Density: {2 * G.edge_count() / (G.node_count() * (G.node_count() - 1)):.2%}")
        
        # Sample edge
        sample_edge = list(G.all_edges())[0]
        print(f"\n📍 Sample Edge: {sample_edge[0]}")
        print(f"   Distance: {sample_edge[1]['distance_m']}m")
        print(f"   Speed: {sample_edge[1]['speed_kph']}km/h")
        print(f"   Time: {time_cost(sample_edge[1]):.1f}s")
        print(f"   Toll: {'Yes' if sample_edge[1]['toll'] else 'No'}")
        
    except FileNotFoundError:
        print("❌ roads.csv not found. Run data_builder.py first!")
