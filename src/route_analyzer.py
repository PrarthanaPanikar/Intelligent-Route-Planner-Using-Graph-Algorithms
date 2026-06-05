"""
==============================================================================
ROUTE ANALYZER: Analyze and Report Route Information
==============================================================================
High-level functions for route analysis, comparison, and report generation.

Features:
- Calculate route statistics (distance, time, cost)
- Compare multiple routes
- Generate formatted route summaries
- Find alternative routes
- Analyze route characteristics

Created for: Intelligent Route Planner - DSA Project
==============================================================================
"""

import math
from .routing_algorithms import dijkstra_shortest_path, astar_shortest_path
from .graph_loader import time_cost, distance_cost, money_cost, eco_cost


class RouteAnalyzer:
    """Analyze routes and generate statistics."""
    
    def __init__(self, graph):
        """
        Initialize analyzer with a road network graph.
        
        Parameters:
        -----------
        graph: RoadNetwork object
        """
        self.graph = graph
    
    def calculate_route_stats(self, path, cost_function):
        """
        Calculate statistics for a given path.
        
        Parameters:
        -----------
        path: List of node IDs
        cost_function: Function to calculate edge cost
        
        Returns:
        --------
        dict: Statistics including distance, time, cost, etc.
        """
        if not path or len(path) < 2:
            return None
        
        total_distance = 0
        total_time = 0
        total_toll = 0
        edge_details = []
        
        # Traverse each edge in path
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge = self.graph.get_edge(u, v)
            
            if edge is None:
                return None
            
            distance = edge["distance_m"]
            time = edge["base_sec"] * edge.get("traffic_factor", 1.0)
            toll = edge["toll"]
            road_class = edge["road_class"]
            speed = edge["speed_kph"]
            
            total_distance += distance
            total_time += time
            total_toll += toll
            
            edge_details.append({
                "from": u,
                "to": v,
                "distance_m": distance,
                "time_sec": time,
                "toll": toll,
                "road_class": road_class,
                "speed_kph": speed
            })
        
        # Calculate eco score (lower is better)
        eco_score = sum(eco_cost(self.graph.get_edge(path[i], path[i+1])) 
                       for i in range(len(path)-1))
        
        return {
            "path": path,
            "num_hops": len(path) - 1,
            "total_distance_m": total_distance,
            "total_distance_km": total_distance / 1000.0,
            "total_time_sec": total_time,
            "total_time_min": total_time / 60.0,
            "total_time_hms": self._format_time(total_time),
            "total_toll": total_toll,
            "eco_score": eco_score,
            "avg_speed_kph": (total_distance / 1000.0) / (total_time / 3600.0) if total_time > 0 else 0,
            "edges": edge_details
        }
    
    def find_shortest_path(self, start, goal, objective="time"):
        """
        Find shortest path for given objective.
        
        Objectives:
        - "time": Fastest route
        - "distance": Shortest distance
        - "money": Lowest toll cost
        - "eco": Most eco-friendly
        
        Parameters:
        -----------
        start: Start node ID
        goal: Goal node ID
        objective: Optimization objective
        
        Returns:
        --------
        dict: Route statistics
        """
        cost_map = {
            "time": time_cost,
            "distance": distance_cost,
            "money": money_cost,
            "eco": eco_cost
        }
        
        cost_fn = cost_map.get(objective, time_cost)
        
        # Use A* for time (has heuristic), Dijkstra for others
        if objective == "time":
            path, _ = astar_shortest_path(self.graph, start, goal, cost_fn)
        else:
            path, _ = dijkstra_shortest_path(self.graph, start, goal, cost_fn)
        
        if path is None:
            return None
        
        return self.calculate_route_stats(path, cost_fn)
    
    def find_alternatives(self, start, goal, num_alternatives=3):
        """
        Find multiple alternative routes using different cost functions.
        
        Parameters:
        -----------
        start: Start node ID
        goal: Goal node ID
        num_alternatives: Number of alternatives to find
        
        Returns:
        --------
        dict: Multiple routes with different objectives
        """
        objectives = ["time", "distance", "money", "eco"][:num_alternatives]
        alternatives = {}
        
        for obj in objectives:
            route = self.find_shortest_path(start, goal, objective=obj)
            if route:
                alternatives[obj] = route
        
        return alternatives
    
    def compare_routes(self, route1, route2):
        """
        Compare two routes and show differences.
        
        Parameters:
        -----------
        route1, route2: Route dicts
        
        Returns:
        --------
        dict: Comparison metrics
        """
        if not route1 or not route2:
            return None
        
        return {
            "distance_diff_m": route2["total_distance_m"] - route1["total_distance_m"],
            "distance_diff_pct": ((route2["total_distance_m"] - route1["total_distance_m"]) / 
                                 route1["total_distance_m"] * 100),
            "time_diff_sec": route2["total_time_sec"] - route1["total_time_sec"],
            "time_diff_pct": ((route2["total_time_sec"] - route1["total_time_sec"]) / 
                             route1["total_time_sec"] * 100),
            "toll_diff": route2["total_toll"] - route1["total_toll"],
            "hops_diff": route2["num_hops"] - route1["num_hops"]
        }
    
    def _format_time(self, seconds):
        """Convert seconds to HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def print_route_summary(self, route, title="Route Summary"):
        """
        Print formatted route summary.
        
        Parameters:
        -----------
        route: Route dict
        title: Header title
        """
        if route is None:
            print("❌ No route found")
            return
        
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
        
        path = route["path"]
        print(f"\n📍 Route Details:")
        print(f"   Start: {path[0]}")
        print(f"   Goal:  {path[-1]}")
        print(f"   Stops: {' → '.join(path)}")
        
        print(f"\n📊 Statistics:")
        print(f"   Distance:  {route['total_distance_km']:.2f} km ({route['total_distance_m']:.0f} m)")
        print(f"   Time:      {route['total_time_min']:.1f} min ({route['total_time_hms']})")
        print(f"   Avg Speed: {route['avg_speed_kph']:.1f} km/h")
        print(f"   Tolls:     {'Yes' if route['total_toll'] > 0 else 'No'} ({route['total_toll']} gates)")
        print(f"   Eco Score: {route['eco_score']:.1f} (lower is better)")
        print(f"   Segments:  {route['num_hops']}")
        
        print(f"\n🛣️  Detailed Route:")
        for i, edge in enumerate(route["edges"], 1):
            print(f"   {i}. {edge['from']} → {edge['to']}")
            toll_str = " | 💰 Toll" if edge['toll'] else ""
            print(f"      Distance: {edge['distance_m']:.0f}m | Time: {edge['time_sec']:.1f}s | Speed: {edge['speed_kph']}km/h | Class: {edge['road_class']}{toll_str}")
        
        print("=" * 70)
    
    def export_route_json(self, route):
        """
        Export route to JSON-compatible dict.
        
        Parameters:
        -----------
        route: Route dict
        
        Returns:
        --------
        dict: JSON-serializable route data
        """
        if route is None:
            return None
        
        return {
            "path": route["path"],
            "summary": {
                "distance_km": round(route["total_distance_km"], 2),
                "distance_m": round(route["total_distance_m"], 0),
                "time_minutes": round(route["total_time_min"], 1),
                "time_seconds": round(route["total_time_sec"], 0),
                "time_formatted": route["total_time_hms"],
                "avg_speed_kph": round(route["avg_speed_kph"], 1),
                "toll_gates": route["total_toll"],
                "eco_score": round(route["eco_score"], 2),
                "segments": route["num_hops"]
            },
            "edges": route["edges"]
        }


if __name__ == "__main__":
    # Example usage
    from graph_loader import load_graph
    
    try:
        G = load_graph("data/roads.csv")
        analyzer = RouteAnalyzer(G)
        
        start, goal = "N0_0", "N4_4"
        
        # Find fastest route
        fastest = analyzer.find_shortest_path(start, goal, "time")
        if fastest:
            analyzer.print_route_summary(fastest, "Fastest Route")
        
        # Find shortest route
        shortest = analyzer.find_shortest_path(start, goal, "distance")
        if shortest:
            analyzer.print_route_summary(shortest, "Shortest Route")
        
        # Find alternatives
        print("\n\n📋 Finding Alternative Routes...")
        alts = analyzer.find_alternatives(start, goal, 4)
        print(f"✅ Found {len(alts)} alternative routes")
        for obj, route in alts.items():
            print(f"\n   {obj.upper()}: {route['total_distance_km']:.2f}km in {route['total_time_min']:.1f}min")
        
    except FileNotFoundError:
        print("❌ roads.csv not found. Run data_builder.py first!")
