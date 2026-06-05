"""
==============================================================================
DATA BUILDER: Generate Sample City Road Network
==============================================================================
This module creates a synthetic city road network as CSV data.
The network represents a 5x5 grid of locations (nodes) connected by roads (edges).
Each road has properties: distance, speed, toll, one-way restrictions, and class.

Created for: Intelligent Route Planner - DSA Project
==============================================================================
"""

import csv
import math
import os


def write_grid_network(n=5, spacing_m=300, output_file="data/roads.csv"):
    """
    Generate a grid-based city road network and save to CSV.
    
    Parameters:
    -----------
    n : int
        Grid size (n x n nodes). Default 5 creates 25 locations.
    spacing_m : int
        Distance between adjacent grid nodes in meters. Default 300m.
    output_file : str
        Output CSV file path.
    
    Returns:
    --------
    None (writes to CSV file)
    
    Edge Attributes:
    ----------------
    - u, v: Node IDs (source, destination)
    - lat_u, lon_u: Latitude, Longitude of source node
    - lat_v, lon_v: Latitude, Longitude of destination node
    - distance_m: Road distance in meters
    - speed_kph: Average speed on road in km/h
    - toll: Toll gate cost (0 = no toll, 1 = toll road)
    - one_way: One-way restriction (0 = bidirectional, 1 = one-way)
    - road_class: Road type (primary, residential, secondary)
    
    Road Network Design:
    --------------------
    1. Regular grid: Residential streets connecting all adjacent nodes
    2. Primary avenue: Faster toll road across row 2
    3. One-way shortcut: Quick diagonal link from (0,0) to (1,1)
    """
    
    rows = []
    
    # Node ID generator
    def node_id(i, j):
        return f"N{i}_{j}"
    
    # Coordinate system
    coords = {}
    base_lat, base_lon = 12.90, 77.50
    
    # Create all nodes with lat/lon coordinates (Bangalore-like)
    print("📍 Creating nodes...")
    for i in range(n):
        for j in range(n):
            # Simulate location coordinates (0.002 degrees ≈ 222 meters at equator)
            lat = base_lat + i * 0.002
            lon = base_lon + j * 0.002
            coords[node_id(i, j)] = (lat, lon)
    
    print(f"✅ Created {n*n} nodes in grid")
    
    # Helper to add road edges
    def add_edge(u, v, dist, speed, toll, one_way, cls):
        """Add a directed edge to the network."""
        lat_u, lon_u = coords[u]
        lat_v, lon_v = coords[v]
        rows.append([u, v, lat_u, lon_u, lat_v, lon_v, dist, speed, toll, one_way, cls])
    
    # 1. Regular grid: Connect adjacent nodes (North-South and East-West)
    print("🛣️  Creating regular grid roads...")
    for i in range(n):
        for j in range(n):
            # East-West connections (horizontal)
            if j + 1 < n:
                u = node_id(i, j)
                v = node_id(i, j + 1)
                add_edge(u, v, spacing_m, 40, 0, 0, "residential")  # Forward
                add_edge(v, u, spacing_m, 40, 0, 0, "residential")  # Backward
            
            # North-South connections (vertical)
            if i + 1 < n:
                u = node_id(i, j)
                v = node_id(i + 1, j)
                add_edge(u, v, spacing_m, 35, 0, 0, "residential")  # Forward
                add_edge(v, u, spacing_m, 35, 0, 0, "residential")  # Backward
    
    # 2. Fast toll avenue (Highway) across row 2
    print("🚗 Creating primary toll avenue...")
    for j in range(n - 1):
        u = node_id(2, j)
        v = node_id(2, j + 1)
        add_edge(u, v, spacing_m, 70, 1, 0, "primary")  # Fast + toll, bidirectional
        add_edge(v, u, spacing_m, 70, 1, 0, "primary")
    
    # 3. One-way shortcut (Emergency/VIP lane)
    print("⚡ Creating one-way shortcut...")
    add_edge(
        node_id(0, 0), 
        node_id(1, 1), 
        int(spacing_m * 1.4), 
        50, 
        0, 
        1, 
        "link"
    )
    
    # 4. Secondary road (slower but no toll) - alternate route
    print("🛣️  Creating secondary roads...")
    for i in range(n - 1):
        u = node_id(i, 0)
        v = node_id(i + 1, 0)
        add_edge(u, v, spacing_m, 30, 0, 0, "secondary")
        add_edge(v, u, spacing_m, 30, 0, 0, "secondary")
    
    # Write to CSV
    print(f"\n📝 Writing {len(rows)} edges to {output_file}...")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        header = "u,v,lat_u,lon_u,lat_v,lon_v,distance_m,speed_kph,toll,one_way,road_class".split(",")
        writer.writerow(header)
        writer.writerows(rows)
    
    print(f"✅ Network saved to {output_file}")
    print(f"\n📊 Network Summary:")
    print(f"   - Grid size: {n}x{n} = {n*n} nodes")
    print(f"   - Total edges: {len(rows)}")
    print(f"   - Road types: residential, primary, secondary, link")
    print(f"   - Network span: ~{spacing_m * (n-1)}m x {spacing_m * (n-1)}m")
    
    return output_file


if __name__ == "__main__":
    # Generate default network
    write_grid_network(n=5, spacing_m=300, output_file="data/roads.csv")
    print("\n✨ Data generation complete! Use this in graph_loader.py")
