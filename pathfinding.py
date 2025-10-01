from collections import deque
import heapq
import randomrandom

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
    
# Depth Limited Search (DLS) phụ trợ cho IDS
def dls( start, goal, maze, limit): 
    ROWS, COLS = len(maze), len(maze[0])
    stack = [(start, [start], 0)] # (node, path, depth)
    visited = set()

    while stack:
        (r, c), path, depth = stack.pop()
        if(r, c) == goal:
            return path
        if depth >= limit:
            continue
        if (r, c) in visited:
            continue
        visited.add((r, c))

        for dr, dc in [(1,0), (0,1), (-1,0), (0, -1)]:
            nr = r+dr
            nc = c+dc
            if 0<= nr <ROWS and 0<= nc < COLS and maze[nr][nc] == 0:
                if (nr,nc) not in visited:
                    stack.append(((nr,nc), path + [(nr,nc)], depth+1))

    return None

#Iterative Deepening Search (IDS)
def ids(start, goal, maze, max_depth=50):
    for depth in range(max_depth+1):
        result = dls(start, goal, maze, depth)
        if result is not None:
            return result
    return []

#Uniform Cost Search( UCS)
def ucs(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    pq = [(0, start, [start])] # cost, node, path
    visited = {}

    while pq:
        cost, (r, c), path = heapq.heappop(pq)
        if(r, c) == goal:
            return path
        if(r, c) in visited and visited[(r, c)] <= cost:
            continue
        visited[(r, c)] = cost

        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr = r+dr
            nc = c+dc
            if 0 <= nr < ROWS and 0<= nc < COLS and maze[nr][nc]==0:
                new_cost = cost+1
                heapq.heappush(pq, (new_cost, (nr, nc), path + [(nr, nc)]))

    return []

## Genetic Algorithm Search
def genetic(start, goal, maze, pop_size=50, generations=200, mutation_rate=0.1, max_steps=100):
    ROWS, COLS = len(maze), len(maze[0])

    # Tạo cá thể: 1 path ngẫu nhiên từ start
    def random_path():
        path = [start]
        current = start
        for _ in range(max_steps):
            if current == goal:
                break
            neighbors = []
            for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
                nr, nc = current[0]+dr, current[1]+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                    neighbors.append((nr,nc))
            if not neighbors:  # nếu kẹt thì dừng
                break
            current = random.choice(neighbors)
            path.append(current)
        return path

    # Fitness: càng gần goal càng tốt, path ngắn hơn cũng tốt
    def fitness(path):
        last = path[-1]
        dist = abs(last[0]-goal[0]) + abs(last[1]-goal[1])  # Manhattan distance
        return 1 / (dist + 1 + len(path)*0.01)

    # Lai ghép (crossover): ghép 2 path tại điểm cắt
    def crossover(p1, p2):
        cut = min(len(p1), len(p2)) // 2
        child = p1[:cut]
        for step in p2:
            if step not in child:
                child.append(step)
        return child

    # Đột biến (mutation): đổi ngẫu nhiên 1 bước trong path
    def mutate(path):
        if len(path) <= 2:
            return path
        if random.random() < mutation_rate:
            idx = random.randint(1, len(path)-1)
            path = path[:idx]
            current = path[-1]
            for _ in range(max_steps - idx):
                if current == goal:
                    break
                neighbors = []
                for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
                    nr, nc = current[0]+dr, current[1]+dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                        neighbors.append((nr,nc))
                if not neighbors:
                    break
                current = random.choice(neighbors)
                path.append(current)
        return path

    # Khởi tạo quần thể
    population = [random_path() for _ in range(pop_size)]

    for gen in range(generations):
        # Nếu có path đến goal thì trả về
        for p in population:
            if p[-1] == goal:
                return p

        # Đánh giá fitness
        scored = [(fitness(p), p) for p in population]
        scored.sort(reverse=True)  # tốt nhất trước

        # Chọn top 20% làm bố mẹ
        parents = [p for _, p in scored[:pop_size//5]]

        # Sinh thế hệ mới
        new_population = parents[:]
        while len(new_population) < pop_size:
            p1, p2 = random.sample(parents, 2)
            child = crossover(p1, p2)
            child = mutate(child)
            new_population.append(child)

        population = new_population

    # Nếu không tìm thấy
    best = max(population, key=fitness)
    return best if best[-1] == goal else []
    
