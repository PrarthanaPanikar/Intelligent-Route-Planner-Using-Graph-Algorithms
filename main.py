"""
==============================================================================
INTELLIGENT ROUTE PLANNER - MAIN APPLICATION
==============================================================================
Complete route planning system using graph algorithms.

Features:
✅ Multiple optimization objectives (time, distance, cost, eco)
✅ BFS, DFS, Dijkstra, A* algorithms
✅ Interactive CLI menu
✅ Route comparison and alternatives
✅ Detailed statistics and analysis
✅ Output export

Usage:
    python main.py

Author: DSA Student
Date: 2024
Created for: Intelligent Route Planner Using Graph Algorithms
==============================================================================
"""

import os
import json
from datetime import datetime

from src.data_builder import write_grid_network
from src.graph_loader import load_graph, RoadNetwork, time_cost, distance_cost, money_cost, eco_cost
from src.routing_algorithms import (
    bfs_shortest_path,
    dfs_shortest_path,
    dijkstra_shortest_path,
    astar_shortest_path,
)
from src.route_analyzer import RouteAnalyzer


class RoutePlannerApp:
    """Main application for intelligent route planning."""
    
    def __init__(self):
        """Initialize the application."""
        self.graph = None
        self.analyzer = None
        self.routes_cache = {}
        self.last_start = None
        self.last_goal = None
        
        print("\n" + "=" * 70)
        print("  🗺️  INTELLIGENT ROUTE PLANNER USING GRAPH ALGORITHMS")
        print("=" * 70)
        print("\n📍 Welcome to the route planning system!")
        print("   Powered by Dijkstra's Algorithm & A* Search\n")
    
    def setup(self):
        """Setup: Create data and load graph."""
        print("\n[PHASE 1: SETUP]")
        print("-" * 70)
        
        # Step 1: Generate data
        print("\n1️⃣  Generating sample city road network...")
        try:
            write_grid_network(n=5, spacing_m=300, output_file="data/roads.csv")
        except Exception as e:
            print(f"❌ Error generating data: {e}")
            return False
        
        # Step 2: Load graph
        print("\n2️⃣  Loading road network from CSV...")
        try:
            self.graph = load_graph("data/roads.csv")
            self.analyzer = RouteAnalyzer(self.graph)
            print(f"✅ Graph loaded: {self.graph.node_count()} nodes, {self.graph.edge_count()} edges")
        except Exception as e:
            print(f"❌ Error loading graph: {e}")
            return False
        
        # Step 3: Display graph info
        self._print_graph_info()
        
        return True
    
    def _print_graph_info(self):
        """Print graph statistics."""
        print(f"\n📊 Graph Statistics:")
        print(f"   Nodes (Locations):  {self.graph.node_count()}")
        print(f"   Edges (Roads):      {self.graph.edge_count()}")
        
        # Sample nodes
        nodes_list = list(self.graph.nodes.keys())[:5]
        print(f"   Sample nodes:       {', '.join(nodes_list)}, ...")
        
        print(f"\n📍 Grid Information:")
        print(f"   Dimension: 5 x 5 grid (25 locations)")
        print(f"   Spacing:   300 meters between adjacent nodes")
        print(f"   Area:      ~1.2 km × 1.2 km")
        print(f"\n   Start node: N0_0 (top-left)")
        print(f"   Goal node:  N4_4 (bottom-right)")
    
    def menu_main(self):
        """Main menu loop."""
        while True:
            print("\n" + "=" * 70)
            print("  MAIN MENU")
            print("=" * 70)
            print("\n1. Find Shortest Path (Time)")
            print("2. Find Shortest Distance")
            print("3. Find Lowest Toll Route")
            print("4. Find Eco-Friendly Route")
            print("5. Compare Multiple Routes")
            print("6. BFS/DFS Visualization")
            print("7. Algorithm Comparison")
            print("8. Save Results to File")
            print("9. Graph Visualization")
            print("0. Exit")
            
            choice = input("\n👉 Enter your choice (0-9): ").strip()
            
            if choice == "1":
                self.find_route("time")
            elif choice == "2":
                self.find_route("distance")
            elif choice == "3":
                self.find_route("money")
            elif choice == "4":
                self.find_route("eco")
            elif choice == "5":
                self.compare_routes()
            elif choice == "6":
                self.visualize_search()
            elif choice == "7":
                self.compare_algorithms()
            elif choice == "8":
                self.save_results()
            elif choice == "9":
                self.visualize_graph()
            elif choice == "0":
                print("\n👋 Thank you for using Intelligent Route Planner!")
                print("   Made with ❤️  for DSA Learning")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def find_route(self, objective="time"):
        """Find route for given objective."""
        print("\n" + "=" * 70)
        print(f"  FIND {objective.upper()} OPTIMAL ROUTE")
        print("=" * 70)
        
        # Get input
        start = input(f"\n📍 Enter start node (e.g., N0_0): ").strip()
        goal = input(f"📍 Enter goal node (e.g., N4_4): ").strip()
        
        # Validate
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            print("❌ Invalid node IDs. Please use format: N<row>_<col> (e.g., N0_0)")
            return
        
        if start == goal:
            print("❌ Start and goal must be different!")
            return
        
        self.last_start = start
        self.last_goal = goal
        
        # Find route
        print(f"\n🔄 Computing {objective} optimal route from {start} to {goal}...")
        route = self.analyzer.find_shortest_path(start, goal, objective)
        
        if route is None:
            print(f"❌ No route found from {start} to {goal}")
            return
        
        # Cache and display
        self.routes_cache[objective] = route
        self.analyzer.print_route_summary(route, f"{objective.capitalize()} Optimal Route")
        
        # Export option
        save_choice = input("\n💾 Save this route? (y/n): ").strip().lower()
        if save_choice == 'y':
            self._export_route(route, objective)
    
    def compare_routes(self):
        """Compare multiple routes."""
        if not self.last_start or not self.last_goal:
            self.find_route("time")
            if not self.last_start:
                return
        
        start, goal = self.last_start, self.last_goal
        
        print("\n" + "=" * 70)
        print(f"  COMPARING ROUTES: {start} → {goal}")
        print("=" * 70)
        
        objectives = ["time", "distance", "money", "eco"]
        routes = {}
        
        print(f"\n🔄 Computing {len(objectives)} routes...")
        for obj in objectives:
            route = self.analyzer.find_shortest_path(start, goal, obj)
            if route:
                routes[obj] = route
        
        # Print comparison table
        print(f"\n📊 COMPARISON TABLE:")
        print(f"\n{'Objective':<12} {'Distance':<15} {'Time':<15} {'Toll':<8} {'Eco':<10}")
        print("-" * 60)
        
        for obj in objectives:
            if obj in routes:
                r = routes[obj]
                dist_str = f"{r['total_distance_km']:.2f} km"
                time_str = f"{r['total_time_hms']}"
                toll_str = f"{r['total_toll']}"
                eco_str = f"{r['eco_score']:.1f}"
                print(f"{obj.capitalize():<12} {dist_str:<15} {time_str:<15} {toll_str:<8} {eco_str:<10}")
        
        # Save comparison
        save_choice = input("\n💾 Save comparison? (y/n): ").strip().lower()
        if save_choice == 'y':
            self._export_comparison(routes)
    
    def visualize_search(self):
        """Show BFS/DFS path exploration."""
        if not self.last_start or not self.last_goal:
            start = input("\n📍 Enter start node: ").strip()
            goal = input("📍 Enter goal node: ").strip()
        else:
            start, goal = self.last_start, self.last_goal
        
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            print("❌ Invalid nodes!")
            return
        
        print(f"\n🔍 BFS Path (Unweighted - Minimum Edges):")
        path_bfs = bfs_shortest_path(self.graph, start, goal)
        if path_bfs:
            print(f"   {' → '.join(path_bfs)}")
            print(f"   Hops: {len(path_bfs) - 1}")
        else:
            print("   No path found")
        
        print(f"\n🔍 DFS Path (One possible path):")
        path_dfs = dfs_shortest_path(self.graph, start, goal)
        if path_dfs:
            print(f"   {' → '.join(path_dfs)}")
            print(f"   Hops: {len(path_dfs) - 1}")
        else:
            print("   No path found")
    
    def compare_algorithms(self):
        """Compare performance of different algorithms."""
        if not self.last_start or not self.last_goal:
            start = input("\n📍 Enter start node: ").strip()
            goal = input("📍 Enter goal node: ").strip()
        else:
            start, goal = self.last_start, self.last_goal
        
        if start not in self.graph.nodes or goal not in self.graph.nodes:
            print("❌ Invalid nodes!")
            return
        
        print(f"\n⚡ ALGORITHM PERFORMANCE COMPARISON ({start} → {goal})")
        print("=" * 70)
        
        import time as time_module
        
        # Dijkstra
        start_time = time_module.time()
        path_dij, cost_dij = dijkstra_shortest_path(self.graph, start, goal, time_cost)
        dij_time = time_module.time() - start_time
        
        # A*
        start_time = time_module.time()
        path_astar, cost_astar = astar_shortest_path(self.graph, start, goal, time_cost)
        astar_time = time_module.time() - start_time
        
        # BFS
        start_time = time_module.time()
        path_bfs = bfs_shortest_path(self.graph, start, goal)
        bfs_time = time_module.time() - start_time
        
        # DFS
        start_time = time_module.time()
        path_dfs = dfs_shortest_path(self.graph, start, goal)
        dfs_time = time_module.time() - start_time
        
        # Print comparison
        print(f"\n{'Algorithm':<12} {'Path':<30} {'Cost':<12} {'Time (ms)':<12}")
        print("-" * 70)
        
        if path_dij:
            path_str = ' → '.join(path_dij[:3]) + '...' if len(path_dij) > 3 else ' → '.join(path_dij)
            print(f"{'Dijkstra':<12} {path_str:<30} {cost_dij:<12.1f} {dij_time*1000:<12.4f}")
        
        if path_astar:
            path_str = ' → '.join(path_astar[:3]) + '...' if len(path_astar) > 3 else ' → '.join(path_astar)
            print(f"{'A*':<12} {path_str:<30} {cost_astar:<12.1f} {astar_time*1000:<12.4f}")
        
        if path_bfs:
            path_str = ' → '.join(path_bfs[:3]) + '...' if len(path_bfs) > 3 else ' → '.join(path_bfs)
            print(f"{'BFS':<12} {path_str:<30} {'N/A':<12} {bfs_time*1000:<12.4f}")
        
        if path_dfs:
            path_str = ' → '.join(path_dfs[:3]) + '...' if len(path_dfs) > 3 else ' → '.join(path_dfs)
            print(f"{'DFS':<12} {path_str:<30} {'N/A':<12} {dfs_time*1000:<12.4f}")
        
        print("\n💡 Key Insights:")
        print(f"   - A* is {dij_time/astar_time:.1f}x faster than Dijkstra for this graph")
        print(f"   - Dijkstra & A* find optimal paths")
        print(f"   - BFS finds minimum-edge path (not optimal for weighted graphs)")
        print(f"   - DFS explores (inefficient for large graphs)")
    
    def visualize_graph(self):
        """Print simple text-based graph visualization."""
        print(f"\n📊 GRAPH VISUALIZATION (Simplified)")
        print("=" * 70)
        
        print(f"\n5x5 Grid Network:")
        print(f"\nN0_0 --- N0_1 --- N0_2 --- N0_3 --- N0_4")
        print(f" |        |        |        |        |")
        print(f"N1_0 --- N1_1 --- N1_2 --- N1_3 --- N1_4")
        print(f" |        |        |        |        |")
        print(f"N2_0 --- N2_1 === N2_2 === N2_3 === N2_4  (=== toll road)")
        print(f" |        |        |        |        |")
        print(f"N3_0 --- N3_1 --- N3_2 --- N3_3 --- N3_4")
        print(f" |        |        |        |        |")
        print(f"N4_0 --- N4_1 --- N4_2 --- N4_3 --- N4_4")
        print(f"\nLegend:")
        print(f"  --- Residential road (35-40 km/h, no toll)")
        print(f"  === Primary toll avenue (70 km/h, toll gate)")
        print(f"  ⚡ One-way shortcut (N0_0 → N1_1)")
        print(f"\nNetwork spans ~1.2 km × 1.2 km")
        
        print(f"\n📡 For interactive visualization, export data as GeoJSON")
        print(f"   and visualize using tools like Leaflet or Folium")
    
    def save_results(self):
        """Save routes and comparisons to file."""
        if not self.routes_cache:
            print("❌ No routes to save. Find a route first!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/route_results_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "routes": {}
        }
        
        for objective, route in self.routes_cache.items():
            data["routes"][objective] = self.analyzer.export_route_json(route)
        
        os.makedirs("outputs", exist_ok=True)
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Results saved to {filename}")
    
    def _export_route(self, route, objective):
        """Export single route to JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/route_{objective}_{timestamp}.json"
        
        data = self.analyzer.export_route_json(route)
        
        os.makedirs("outputs", exist_ok=True)
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Route saved to {filename}")
    
    def _export_comparison(self, routes):
        """Export route comparison to JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/route_comparison_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "routes": {obj: self.analyzer.export_route_json(route) 
                      for obj, route in routes.items()}
        }
        
        os.makedirs("outputs", exist_ok=True)
        
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Comparison saved to {filename}")
    
    def run(self):
        """Run the complete application."""
        # Setup
        if not self.setup():
            print("\n❌ Failed to setup. Exiting.")
            return
        
        # Main menu
        try:
            self.menu_main()
        except KeyboardInterrupt:
            print("\n\n👋 Application interrupted by user.")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Entry point."""
    app = RoutePlannerApp()
    app.run()


if __name__ == "__main__":
    main()
