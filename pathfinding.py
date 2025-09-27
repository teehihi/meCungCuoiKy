from collections import deque
import heapq

# Heuristic (Manhattan distance)
def hx(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Breadth-First Search (BFS)
def bfs(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    q = deque([(start, [start])])
    visited = {start}
    while q:
        (r, c), path = q.popleft()
        if (r, c) == goal:
            return path
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr,nc) not in visited:
                visited.add((nr,nc))
                q.append(((nr,nc), path + [(nr,nc)]))
    return []

# Depth-First Search (DFS)
def dfs(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    stack = [(start, [start])]
    visited = set()

    while stack:
        (r, c), path = stack.pop()
        if (r, c) == goal:
            return path
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                if (nr, nc) not in visited:
                    stack.append(((nr, nc), path + [(nr, nc)]))
    return []

# Greedy Best-First Search
def greedy(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    pq = [(hx(start, goal), start, [start])]
    visited = set()

    while pq:
        _, (r, c), path = heapq.heappop(pq)
        if (r, c) == goal:
            return path
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr,nc) not in visited:
                heapq.heappush(pq, (hx((nr,nc), goal), (nr,nc), path+[(nr,nc)]))
    return []

# A* Search
def astar(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    pq = [(hx(start, goal), 0, start, [start])]  # (f=g+h, g, node, path)
    visited = set()

    while pq:
        f, g, (r, c), path = heapq.heappop(pq)
        if (r, c) == goal:
            return path
        if (r, c) in visited:
            continue
        visited.add((r, c))
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                if (nr, nc) not in visited:
                    g2 = g + 1
                    f2 = g2 + hx((nr, nc), goal)
                    heapq.heappush(pq, (f2, g2, (nr, nc), path+[(nr, nc)]))
    return []

import math
import random

# Hill Climbing
def hill_climbing(start, goal, maze, max_steps=1000):
    ROWS, COLS = len(maze), len(maze[0])
    current = start
    path = [current]

    for _ in range(max_steps):
        if current == goal:
            return path
        neighbors = []
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = current[0]+dr, current[1]+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                neighbors.append((nr,nc))

        if not neighbors:
            break

        # chọn neighbor có heuristic nhỏ nhất (tốt nhất)
        best = min(neighbors, key=lambda x: hx(x, goal))
        if hx(best, goal) >= hx(current, goal):  # không tiến bộ thì dừng
            break

        current = best
        path.append(current)

    return path if current == goal else []

# Simulated Annealing
def simulated_annealing(start, goal, maze, max_steps=1000, T=100.0, alpha=0.99):
    ROWS, COLS = len(maze), len(maze[0])
    current = start
    path = [current]

    for _ in range(max_steps):
        if current == goal:
            return path

        neighbors = []
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = current[0]+dr, current[1]+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                neighbors.append((nr,nc))

        if not neighbors:
            break

        next_node = random.choice(neighbors)
        deltaE = hx(current, goal) - hx(next_node, goal)

        if deltaE > 0:  # tốt hơn
            current = next_node
            path.append(current)
        else:  # kém hơn nhưng có thể nhận theo xác suất
            prob = math.exp(deltaE / T) if T > 0 else 0
            if random.random() < prob:
                current = next_node
                path.append(current)

        T *= alpha  # giảm nhiệt độ dần

    return path if current == goal else []