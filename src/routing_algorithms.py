"""
==============================================================================
ROUTING ALGORITHMS: BFS, DFS, Dijkstra's Algorithm, A* Search
==============================================================================
Core shortest path algorithms for route planning.

Algorithms Implemented:
- BFS (Breadth-First Search): Find path with minimum edges
- DFS (Depth-First Search): Explore all paths
- Dijkstra: Find shortest path (weighted graph)
- A*: Heuristic-based shortest path search

Time Complexities:
- BFS: O(V + E)
- DFS: O(V + E)
- Dijkstra: O((V + E) log V) with min-heap
- A*: O((V + E) log V) with good heuristic

Created for: Intelligent Route Planner - DSA Project
==============================================================================
"""

import heapq
import math
from collections import deque, defaultdict


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate great-circle distance between two points (lat, lon).
    
    Used for A* heuristic: Straight-line distance to goal.
    
    Parameters:
    -----------
    lat1, lon1: Source coordinates (degrees)
    lat2, lon2: Destination coordinates (degrees)
    
    Returns:
    --------
    float: Distance in meters
    """
    R = 6371000  # Earth radius in meters
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def bfs_shortest_path(graph, start, goal):
    """
    Breadth-First Search: Find path with minimum number of edges.
    
    Algorithm:
    ----------
    1. Initialize queue with start node
    2. Mark start as visited
    3. While queue not empty:
       - Dequeue front node
       - If goal reached, reconstruct path
       - Enqueue all unvisited neighbors
    4. Return path or None if no path exists
    
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    
    When to use BFS:
    - Unweighted graphs (all edges have same cost)
    - Find minimum edge-count path
    - Not typical for road networks (edges have different weights)
    
    Parameters:
    -----------
    graph: RoadNetwork object
    start: Start node ID
    goal: Goal node ID
    
    Returns:
    --------
    list: Path (sequence of node IDs) or None if not found
    """
    if start == goal:
        return [start]
    
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    
    while queue:
        node = queue.popleft()
        
        # Explore all neighbors
        for neighbor in graph.get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                
                # Goal reached
                if neighbor == goal:
                    # Reconstruct path
                    path = []
                    current = goal
                    while current is not None:
                        path.append(current)
                        current = parent[current]
                    return list(reversed(path))
                
                queue.append(neighbor)
    
    return None  # No path found


def dfs_shortest_path(graph, start, goal, path=None, visited=None):
    """
    Depth-First Search: Explore all paths (not guaranteed shortest for weighted graphs).
    
    Algorithm:
    ----------
    1. Mark current node as visited
    2. If current is goal, return path
    3. For each unvisited neighbor:
       - Recursively call DFS
       - If goal found, return path
    4. Backtrack if no path found
    
    Time Complexity: O(V + E) or O(V!) in worst case
    Space Complexity: O(V) for recursion stack
    
    When to use DFS:
    - Explore all possible paths
    - Topological sorting
    - Cycle detection
    - Not suitable for shortest path in weighted graphs
    
    Parameters:
    -----------
    graph: RoadNetwork object
    start: Start node ID
    goal: Goal node ID
    path: Current path (for recursion)
    visited: Set of visited nodes (for recursion)
    
    Returns:
    --------
    list: One possible path or None if not found
    """
    if path is None:
        path = []
    if visited is None:
        visited = set()
    
    path = path + [start]
    visited.add(start)
    
    # Goal reached
    if start == goal:
        return path
    
    # Explore neighbors
    for neighbor in graph.get_neighbors(start):
        if neighbor not in visited:
            new_path = dfs_shortest_path(graph, neighbor, goal, path, visited)
            if new_path is not None:
                return new_path
    
    return None  # No path found


def dijkstra_shortest_path(graph, start, goal, cost_function):
    """
    Dijkstra's Algorithm: Find shortest path in weighted graph.
    
    Developed by Edsger Dijkstra (1956), fundamental to GPS/routing systems.
    
    Algorithm:
    ----------
    1. Initialize distances: dist[start] = 0, others = ∞
    2. Use min-heap (priority queue) to always process nearest unvisited node
    3. For each node, update distances to neighbors (relaxation)
    4. Continue until goal reached or all reachable nodes processed
    
    Key Insight (Relaxation):
    if dist[u] + cost(u,v) < dist[v]:
        dist[v] = dist[u] + cost(u,v)
        parent[v] = u
    
    Time Complexity: O((V + E) log V) with min-heap
    Space Complexity: O(V)
    
    Guarantees:
    - Optimal path (if all edge weights non-negative)
    - Works with any cost function (time, distance, money)
    
    Real-World Usage:
    - Google Maps: Dijkstra variant (fast)
    - GPS Navigation: Dijkstra + A* heuristic
    - Uber/Lyft: Modified Dijkstra with dynamic weights
    
    Parameters:
    -----------
    graph: RoadNetwork object
    start: Start node ID
    goal: Goal node ID
    cost_function: Function(edge_dict) -> float (cost value)
    
    Returns:
    --------
    tuple: (path, total_cost) or (None, None) if not found
    """
    if start == goal:
        return [start], 0
    
    # Initialize distances
    distances = {node: float('inf') for node in graph.nodes}
    distances[start] = 0
    parent = {start: None}
    
    # Min-heap: (distance, node)
    pq = [(0, start)]
    visited = set()
    
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        # Already processed with shorter distance
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        # Goal reached
        if current_node == goal:
            # Reconstruct path
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = parent[node]
            return list(reversed(path)), distances[goal]
        
        # Explore neighbors (relaxation step)
        for neighbor in graph.get_neighbors(current_node):
            if neighbor not in visited:
                edge = graph.get_edge(current_node, neighbor)
                edge_cost = cost_function(edge)
                new_dist = distances[current_node] + edge_cost
                
                # Update if shorter path found
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    parent[neighbor] = current_node
                    heapq.heappush(pq, (new_dist, neighbor))
    
    return None, None  # No path found


def astar_shortest_path(graph, start, goal, cost_function, heuristic_function=None):
    """
    A* Search: Optimal shortest path with heuristic guidance.
    
    Algorithm:
    ----------
    1. Like Dijkstra, but prioritizes nodes by f(n) = g(n) + h(n)
       where:
       - g(n): Actual cost from start to n
       - h(n): Heuristic estimate from n to goal
    
    2. This biases search toward goal, reducing nodes explored
    3. If heuristic is admissible (never overestimates), A* finds optimal path
    
    Time Complexity: O((V + E) log V) typical; better with good heuristic
    Space Complexity: O(V)
    
    Key Advantage over Dijkstra:
    - Dijkstra: Explores in all directions (sphere expansion)
    - A*: Explores toward goal (cone expansion)
    
    Heuristic: Straight-line distance to goal (admissible for road networks)
    
    When to use A*:
    - Spatial graphs (maps, game grids)
    - Single destination known
    - Need faster search than Dijkstra
    
    Real-World: GPS devices use A* variant for speed
    
    Parameters:
    -----------
    graph: RoadNetwork object
    start: Start node ID
    goal: Goal node ID
    cost_function: Function(edge_dict) -> float
    heuristic_function: Function(graph, node1, node2) -> float (optional)
    
    Returns:
    --------
    tuple: (path, total_cost) or (None, None) if not found
    """
    
    # Default heuristic: straight-line distance converted to time
    if heuristic_function is None:
        def heuristic_function(node1, node2):
            if node1 not in graph.node_coords or node2 not in graph.node_coords:
                return 0
            
            lat1, lon1 = graph.node_coords[node1]
            lat2, lon2 = graph.node_coords[node2]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            
            # Assume max speed 80 km/h = 22.22 m/s
            max_speed_ms = 80 * 1000 / 3600
            return distance / max_speed_ms
    
    if start == goal:
        return [start], 0
    
    # Initialize
    g_scores = {node: float('inf') for node in graph.nodes}
    g_scores[start] = 0
    parent = {start: None}
    
    # Priority queue: (f_score, counter, node)
    # Counter breaks ties consistently
    pq = [(0, 0, start)]
    visited = set()
    counter = 1
    
    while pq:
        _, _, current_node = heapq.heappop(pq)
        
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        # Goal reached
        if current_node == goal:
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = parent[node]
            return list(reversed(path)), g_scores[goal]
        
        # Explore neighbors
        for neighbor in graph.get_neighbors(current_node):
            if neighbor not in visited:
                edge = graph.get_edge(current_node, neighbor)
                edge_cost = cost_function(edge)
                tentative_g = g_scores[current_node] + edge_cost
                
                if tentative_g < g_scores[neighbor]:
                    parent[neighbor] = current_node
                    g_scores[neighbor] = tentative_g
                    h_score = heuristic_function(neighbor, goal)
                    f_score = tentative_g + h_score
                    heapq.heappush(pq, (f_score, counter, neighbor))
                    counter += 1
    
    return None, None  # No path found


def reconstruct_path(parent, start, goal):
    """
    Reconstruct path from parent pointers.
    
    Parameters:
    -----------
    parent: Dict mapping node to parent node
    start: Start node
    goal: Goal node
    
    Returns:
    --------
    list: Path from start to goal
    """
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent.get(current)
    return list(reversed(path))


if __name__ == "__main__":
    # Example: Test algorithms on a simple graph
    print("Dijkstra's Algorithm - Basic Test")
    print("=" * 50)

    from .graph_loader import load_graph, time_cost

    try:
        G = load_graph("data/roads.csv")

        start, goal = "N0_0", "N4_4"

        # Test Dijkstra
        path, cost = dijkstra_shortest_path(G, start, goal, time_cost)
        if path:
            print(f"\n✅ Dijkstra's Shortest Path:")
            print(f"   From: {start} → To: {goal}")
            print(f"   Path: {' → '.join(path)}")
            print(f"   Cost: {cost:.1f} seconds")
            print(f"   Hops: {len(path) - 1}")
        else:
            print(f"❌ No path found from {start} to {goal}")

        # Test A*
        path_astar, cost_astar = astar_shortest_path(G, start, goal, time_cost)
        if path_astar:
            print(f"\n✅ A* Shortest Path:")
            print(f"   Path: {' → '.join(path_astar)}")
            print(f"   Cost: {cost_astar:.1f} seconds")

        # Test BFS
        path_bfs = bfs_shortest_path(G, start, goal)
        if path_bfs:
            print(f"\n✅ BFS Path (minimum edges):")
            print(f"   Path: {' → '.join(path_bfs)}")
            print(f"   Edges: {len(path_bfs) - 1}")

    except FileNotFoundError:
        print("❌ roads.csv not found. Run data_builder.py first!")
