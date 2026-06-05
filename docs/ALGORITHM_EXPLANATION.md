# Algorithm Explanation: Dijkstra's & A* Search

## 📖 Complete Guide to Shortest Path Algorithms

---

## 1. Dijkstra's Algorithm - Deep Dive

### What is It?

**Dijkstra's Shortest Path Algorithm** finds the shortest path between nodes in a weighted graph where all edge weights are non-negative.

Developed by **Edsger Dijkstra** in 1956, it's one of the most important algorithms in computer science and forms the basis of GPS navigation systems worldwide.

### Problem It Solves

**Single-Source Shortest Path Problem:**
```
Given: Weighted graph G(V, E, W), source node s
Find: Shortest path from s to every other node
      (or specifically to destination d)

Where "shortest" = minimum total weight
```

### How Dijkstra's Works - Step by Step

#### Phase 1: Initialization
```
dist[start] = 0
dist[all other nodes] = ∞
unvisited = {all nodes}
parent[start] = None
priority_queue.push((0, start))
```

#### Phase 2: Main Loop - Greedy Selection
```
While priority_queue not empty:
  1. Extract node 'u' with minimum distance
  2. Mark u as visited (final distance found)
  3. For each neighbor 'v' of u:
       If v not visited:
         a. Calculate: new_dist = dist[u] + weight(u,v)
         b. If new_dist < dist[v]:
            - dist[v] = new_dist
            - parent[v] = u
            - priority_queue.push((new_dist, v))
  4. If v == destination: STOP (found shortest path!)
```

#### Phase 3: Path Reconstruction
```
path = []
current = destination
While current != None:
  path.prepend(current)
  current = parent[current]
Return path
```

### Concrete Example

**Simple Graph:**
```
        10
    A -------> B
    |          ^
    | 5      6 |
    |          |
    v          |
    C -------> D
         2
```

**Dijkstra from A to B:**

| Step | Current | dist[A] | dist[B] | dist[C] | dist[D] | Action |
|------|---------|---------|---------|---------|---------|--------|
| 0 | - | 0 | ∞ | ∞ | ∞ | Initialize |
| 1 | A | 0 | 10 | 5 | ∞ | Visit A, relax B(10), C(5) |
| 2 | C | 0 | 10 | 5 | 7 | Visit C, relax D(2+5=7) |
| 3 | D | 0 | 8 | 5 | 7 | Visit D, relax B(6+2=8<10) |
| 4 | B | 0 | 8 | 5 | 7 | Visit B - DONE! |

**Result:**
- Shortest path A→B: 8 (via A→C→D→B)
- Not the direct edge (10)!

### Why Does It Work?

**Key Insight: Greedy Choice Property**

Once we visit a node and set its distance, that distance is FINAL and optimal.

**Proof:**
```
1. We always process node with MINIMUM known distance
2. Let's say we mark dist[u] as final
3. Could there be a shorter path to u via some unvisited node v?
4. NO! Because:
   - dist[v] ≥ dist[u] (v's distance is ≥ current min we extracted)
   - Any path u through v costs ≥ dist[u] + edge(v,u)
   - But we already have path of cost dist[u]
5. Therefore, dist[u] is definitely the shortest path to u

This is why we can "finalize" nodes immediately.
```

### Why Only Non-Negative Weights?

**Problem with Negative Weights:**
```
With negative edges, the greedy choice fails:

Graph:
  A --(5)--> B --(−10)--> C

Dijkstra would:
1. Mark B final at dist[B] = 5
2. Never consider B again
3. But path A → B → C = 5 − 10 = −5 < 5!
4. We missed the shorter path!

Negative cycles make it even worse (infinite improvements)
```

**Solution:** Use **Bellman-Ford algorithm** for negative weights (slower: O(VE))

### Time Complexity Analysis

Using **Binary Min-Heap** priority queue:

```
Operation              Count    Complexity    Total
─────────────────────────────────────────────────────
Initialize            O(V)     O(1)          O(V)
Extract-Min           O(V)     O(log V)      O(V log V)
Decrease-Key          O(E)     O(log V)      O(E log V)
─────────────────────────────────────────────────────
TOTAL                                        O((V+E) log V)
```

**Practical Numbers:**
```
Cities (V)          Roads (E)         Operations
─────────────────────────────────────────────
100 cities          400 roads         ~2,000
1,000 cities        5,000 roads       ~50,000
1,000,000 cities    20M roads         ~600 billion ⚠️ (still need optimization)
```

### Space Complexity

```
Data Structure        Space Usage
────────────────────────────────
Distance array        O(V)
Parent array          O(V)
Priority queue        O(V)
Graph (adj list)      O(V + E)
────────────────────────────────
TOTAL                 O(V + E)
```

### Implementation - Code Walkthrough

```python
def dijkstra(graph, start, goal, cost_function):
    # Step 1: Initialize
    distances = {node: float('inf') for node in graph.nodes}
    distances[start] = 0
    parent = {start: None}
    
    # Min-heap stores (distance, node)
    pq = [(0, start)]
    visited = set()
    
    # Step 2: Main loop - process nodes in order of distance
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        # Already processed via shorter path
        if current in visited:
            continue
        
        visited.add(current)
        
        # Goal reached - shortest path found!
        if current == goal:
            path = reconstruct_path(parent, start, goal)
            return path, distances[goal]
        
        # Step 3: Relax edges - try to improve neighbors
        for neighbor in graph.neighbors(current):
            if neighbor not in visited:
                edge = graph.get_edge(current, neighbor)
                edge_cost = cost_function(edge)
                new_dist = distances[current] + edge_cost
                
                # Found shorter path to neighbor
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    parent[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))
    
    return None  # No path found
```

**Line-by-line explanation:**
- `distances[start] = 0`: Only start has cost 0
- `pq = [(0, start)]`: Priority queue sorted by distance
- `heappop(pq)`: Get node with minimum distance
- `if current in visited: continue`: Skip if already finalized
- `visited.add(current)`: Mark as finalized
- `edge_cost = cost_function(edge)`: Can use any cost (time, distance, etc.)
- `new_dist = distances[current] + edge_cost`: Calculate new path cost
- `if new_dist < distances[neighbor]`: Found improvement?
- `heappush(pq, ...)`: Add to queue for later processing

---

## 2. A* Search Algorithm

### What is It?

**A* = Dijkstra + Heuristic**

Combines Dijkstra's optimal properties with intelligent goal-directed search using a heuristic function to prune unnecessary node exploration.

### Why A* Over Dijkstra?

**Dijkstra's Limitation:**
```
Without direction to goal, explores in ALL directions equally
Like expanding a circle around start → explores everywhere

Dijkstra's exploration:
            N1
          /    \
    N2 - Start - N3
        \    /
            N4
```

**A* Solution:**
```
Uses heuristic to guess direction → biases toward goal
Like expanding a cone toward goal → explores smarter

A* exploration (with goal info):
            N1
           /
    N2 - Start -----> GOAL
           \
            N3
```

### The A* Evaluation Function

```
f(n) = g(n) + h(n)

where:
  f(n) = total estimated cost through node n
  g(n) = actual cost from start to n (known)
  h(n) = heuristic estimate from n to goal (unknown)
```

**Dijkstra (for comparison):**
```
f(n) = g(n)  [only considers cost from start]
```

**A* is Dijkstra with an extra term:**
```
f(n) = g(n) + h(n)  [adds goal direction]
```

### A* Algorithm

```
Initialize:
  open_set = {start}
  closed_set = {}
  g_score[start] = 0
  h_score[start] = heuristic(start, goal)
  f_score[start] = h_score[start]

Main Loop:
  While open_set not empty:
    1. current = node in open_set with lowest f_score
    2. If current == goal: reconstruct and return path
    3. Move current from open to closed set
    4. For each neighbor of current:
       a. If neighbor in closed_set: skip
       b. tentative_g = g_score[current] + cost(current, neighbor)
       c. If neighbor not in open_set: add it
       d. If tentative_g < g_score[neighbor]:
          - Update g_score[neighbor]
          - Update f_score[neighbor] = g_score + h_score
  
  Return: No path found
```

### The Heuristic Function

**Key Requirement:** Heuristic must be **admissible**
```
h(n) ≤ actual_cost(n, goal)
Heuristic never overestimates true cost
```

**Why admissible?** Ensures A* finds optimal path

### Our Heuristic: Straight-Line Distance

```python
def heuristic(node1, node2):
    """
    Straight-line distance converted to time units
    
    This is admissible because:
    - Straight line is shortest possible distance
    - Actual road distance ≥ straight line
    - Therefore: h(n) ≤ actual_cost(n, goal)
    """
    lat1, lon1 = coordinates[node1]
    lat2, lon2 = coordinates[node2]
    
    # Haversine distance in meters
    distance = haversine(lat1, lon1, lat2, lon2)
    
    # Estimate time at max speed (e.g., 80 km/h)
    max_speed_ms = 80 * 1000 / 3600  # = 22.22 m/s
    estimated_time = distance / max_speed_ms
    
    return estimated_time
```

### Visualization: Dijkstra vs A*

**Test:** Find shortest path from A to J

**Dijkstra exploration:**
```
Nodes explored: {A, B, C, D, E, F, G, H, I, J}  [10 nodes]
Resembles: Circle expanding outward
```

**A* exploration (with heuristic):**
```
Nodes explored: {A, B, C, G, J}  [5 nodes]
Resembles: Cone pointing toward goal
Speedup: 2x-10x fewer nodes
```

### Time Complexity

```
With admissible heuristic:
  - Worst case: O((V + E) log V)  [same as Dijkstra]
  - Average case: Much better!    [10-100x on spatial graphs]
  - With bad heuristic: O((V + E)²)  [worse than Dijkstra!]

Depends entirely on heuristic quality
```

### When to Use A*

✅ **Good for A*:**
- Single destination known
- Spatial graphs (maps, grids, games)
- Good heuristic available
- Performance critical
- Real-world routing

❌ **Better to use Dijkstra:**
- All-pairs shortest paths
- Multi-destination queries
- No good heuristic
- Simplicity matters
- Graph not spatial

### Real-World: GPS Devices

Modern GPS uses **Bidirectional A*:**
```
Search from both start AND goal simultaneously
Meet in middle
Complexity: √(V + E) log V (square root improvement!)
Practical: 10x-100x faster than regular A*
```

---

## 3. BFS vs DFS vs Dijkstra vs A*

### Comparison Table

| Property | BFS | DFS | Dijkstra | A* |
|----------|-----|-----|----------|-----|
| **Graph Type** | Unweighted | Any | Weighted | Weighted |
| **Optimality** | Min edges | Any path | Optimal | Optimal* |
| **Time** | O(V+E) | O(V+E) | O((V+E)log V) | O((V+E)log V)* |
| **Space** | O(V) | O(V) | O(V) | O(V) |
| **Uses** | Shortest edges | Path finding | GPS | GPS (faster) |
| **Heuristic** | None | None | None | Required |
| **Best for** | Grid levels | Maze solving | Routing | Real maps |

### When to Use Each

```
Unweighted graph?
  └─→ Use BFS (simplest, optimal for edges)

Weighted graph, all edges important?
  └─→ Use Dijkstra (proven optimal)

Weighted graph, spatial, single destination?
  └─→ Use A* (faster with heuristic)

Need ANY path (not shortest)?
  └─→ Use DFS (memory efficient)

Negative edge weights?
  └─→ Use Bellman-Ford (slower but correct)
```

---

## 4. Common Mistakes & Pitfalls

### Mistake 1: Relaxing After Visiting

❌ **Wrong:**
```python
for neighbor in graph.neighbors(current):
    visited.add(neighbor)  # Mark as visited TOO EARLY
    # Now we can't improve it!
```

✅ **Correct:**
```python
for neighbor in graph.neighbors(current):
    if neighbor not in visited:  # Only relax unvisited
        # Improve distance if possible
```

### Mistake 2: Using Dijkstra with Negative Edges

❌ **Wrong:**
```python
# Will fail with negative weights!
dijkstra(graph_with_negative_edges, start, goal)
```

✅ **Correct:**
```python
# Use Bellman-Ford instead
bellman_ford(graph_with_negative_edges, start, goal)
```

### Mistake 3: Bad Heuristic in A*

❌ **Wrong:**
```python
def bad_heuristic(n1, n2):
    return 1000  # Overestimates! Not admissible
```

✅ **Correct:**
```python
def good_heuristic(n1, n2):
    distance = haversine(n1.lat, n1.lon, n2.lat, n2.lon)
    return distance / max_speed  # Never overestimates
```

### Mistake 4: Not Reconstructing Path

❌ **Wrong:**
```python
path, cost = dijkstra(graph, start, goal)
# path = None, only return final cost
```

✅ **Correct:**
```python
parent = {}  # Track where each node came from
# ... during algorithm ...
# At end: reconstruct_path(parent, start, goal)
```

### Mistake 5: Infinite Loop in Priority Queue

❌ **Wrong:**
```python
while pq:  # Processes all nodes, even visited ones
    dist, node = heappop(pq)
    # No check for already visited
```

✅ **Correct:**
```python
visited = set()
while pq:
    dist, node = heappop(pq)
    if node in visited:
        continue  # Skip already processed
    visited.add(node)
```

---

## 5. Interview Q&A

**Q: Explain Dijkstra in 1 minute**

"Dijkstra finds shortest paths using a greedy approach. Start with distance 0 at source, ∞ elsewhere. Repeatedly pick the unvisited node with minimum distance, update its neighbors, and mark it as final. Once visited, a node's distance never changes. Uses a min-heap for O((V+E) log V) complexity. Works only for non-negative weights."

**Q: Why is A* faster than Dijkstra?**

"A* adds a heuristic function h(n) that estimates remaining distance to goal. By prioritizing nodes closer to goal, A* explores fewer nodes. If heuristic is admissible (never overestimates), A* still finds optimal path but much faster. Dijkstra explores equally in all directions; A* points like a cone toward goal."

**Q: Can Dijkstra handle negative edges?**

"No. Dijkstra's greedy choice fails with negative edges because finalizing a node doesn't guarantee it won't get a shorter path later. Negative cycles make it impossible. Use Bellman-Ford instead for negative weights; it's slower O(VE) but correct."

---

**Resource:** Code implementations in `routing_algorithms.py`
