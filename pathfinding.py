from collections import deque
import heapq
import random
import math
import time

# ================= Helper =================
def print_maze_step(maze, path=None, current=None, start=None, goal=None):
    if path is None:
        path = []
    display = ""
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            if (r,c) == start:
                display += "S"
            elif (r,c) == goal:
                display += "G"
            elif (r,c) == current:
                display += "X"
            elif (r,c) in path:
                display += "."
            elif maze[r][c] == 1:
                display += "#"
            else:
                display += " "
        display += "\n"
    print(display)

def hx(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ================= BFS =================
def bfs(start, goal, maze, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    q = deque([(start, [start])])
    visited = {start}
    while q:
        (r, c), path = q.popleft()
        if visualize:
            print_maze_step(maze, path, current=(r,c), start=start, goal=goal)
            time.sleep(delay)
        if (r, c) == goal:
            return path
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0 and (nr,nc) not in visited:
                visited.add((nr,nc))
                q.append(((nr,nc), path+[(nr,nc)]))
    return []

# ================= DFS =================
def dfs(start, goal, maze, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    stack = [(start, [start])]
    visited = set()
    while stack:
        (r,c), path = stack.pop()
        if (r,c) in visited:
            continue
        visited.add((r,c))
        if visualize:
            print_maze_step(maze, path, current=(r,c), start=start, goal=goal)
            time.sleep(delay)
        if (r,c) == goal:
            return path
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0 and (nr,nc) not in visited:
                stack.append(((nr,nc), path+[(nr,nc)]))
    return []

# ================= Greedy =================
def greedy(start, goal, maze, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    pq = [(hx(start, goal), start, [start])]
    visited = set()
    while pq:
        _, (r,c), path = heapq.heappop(pq)
        if (r,c) in visited:
            continue
        visited.add((r,c))
        if visualize:
            print_maze_step(maze, path, current=(r,c), start=start, goal=goal)
            time.sleep(delay)
        if (r,c) == goal:
            return path
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0 and (nr,nc) not in visited:
                heapq.heappush(pq, (hx((nr,nc), goal), (nr,nc), path+[(nr,nc)]))
    return []
# ================= A* =================
def astar(start, goal, maze):
    """
    A* tìm đường đi trên lưới maze.
    Trả về list path từ start -> goal, hoặc None nếu không tìm được.
    maze: 2D list, 0 = ô trống, 1 = tường
    start, goal: tuple (row, col)
    """
    ROWS, COLS = len(maze), len(maze[0])

    def heuristic(a, b):
        # Manhattan distance
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    def neighbors(r, c):
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                yield (nr, nc)

    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start))
    open_set_nodes = {start}  # track các node đang trong heap
    came_from = {}
    g_score = {start: 0}

    while open_set:
        f, g, current = heapq.heappop(open_set)
        open_set_nodes.remove(current)

        if current == goal:
            # build path từ start -> goal
            path = []
            tmp = current
            while tmp in came_from:
                path.append(tmp)
                tmp = came_from[tmp]
            path.append(start)
            path.reverse()
            return path

        for nxt in neighbors(*current):
            tentative_g = g_score[current] + 1
            if nxt not in g_score or tentative_g < g_score[nxt]:
                came_from[nxt] = current
                g_score[nxt] = tentative_g
                f_score = tentative_g + heuristic(nxt, goal)
                if nxt not in open_set_nodes:
                    heapq.heappush(open_set, (f_score, tentative_g, nxt))
                    open_set_nodes.add(nxt)

    return None  # không tìm được đường đi


# ================= Hill Climbing =================
def hill_climbing(start, goal, maze, visualize=False, delay=0.05, max_steps=500):
    ROWS, COLS = len(maze), len(maze[0])
    current = start
    path = [current]

    for _ in range(max_steps):
        if current == goal:
            return path

        neighbors = [(current[0]+dr, current[1]+dc)
                     for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]
                     if 0 <= current[0]+dr < ROWS and 0 <= current[1]+dc < COLS and maze[current[0]+dr][current[1]+dc] == 0]

        if not neighbors:
            break

        best = min(neighbors, key=lambda x: hx(x, goal))
        if hx(best, goal) >= hx(current, goal):
            break

        current = best
        path.append(current)

        if visualize:
            print_maze_step(maze, path, current=current, start=start, goal=goal)
            time.sleep(delay)

    return path

# ================= Backtracking =================
def backtracking(start, goal, maze, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    path = []
    visited = set()
    def bt(r,c):
        if (r,c)==goal:
            path.append((r,c))
            return True
        if (r,c) in visited:
            return False
        visited.add((r,c))
        path.append((r,c))
        if visualize:
            print_maze_step(maze, path, current=(r,c), start=start, goal=goal)
            time.sleep(delay)
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0:
                if bt(nr,nc):
                    return True
        path.pop()
        return False
    if bt(start[0], start[1]):
        return path
    return []

# ================= Forward Checking =================
def forward_checking(start, goal, maze):
    """
    Forward Checking tìm đường đi từ start -> goal.
    Trả về path dưới dạng list, giống Backtracking.
    """
    ROWS, COLS = len(maze), len(maze[0])
    path = []
    visited = set()

    def domain_ok(r, c):
        # Kiểm tra có ô lân cận chưa visited và không phải tường
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr,nc) not in visited:
                return True
        return False

    def fc(r, c):
        if (r,c) == goal:
            path.append((r,c))
            return True
        if (r,c) in visited:
            return False
        visited.add((r,c))
        path.append((r,c))
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr,nc) not in visited:
                if domain_ok(nr, nc):
                    if fc(nr, nc):
                        return True
        path.pop()
        return False

    if fc(start[0], start[1]):
        return path
    return []  # không tìm thấy đường đi
# ================= UCS =================
def ucs(start, goal, maze, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    pq = [(0, start, [start])]
    visited = {}
    while pq:
        cost, (r,c), path = heapq.heappop(pq)
        if (r,c) in visited and visited[(r,c)] <= cost:
            continue
        visited[(r,c)] = cost
        if visualize:
            print_maze_step(maze, path, current=(r,c), start=start, goal=goal)
            time.sleep(delay)
        if (r,c) == goal:
            return path
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0:
                heapq.heappush(pq, (cost+1, (nr,nc), path+[(nr,nc)]))
    return []

# ================= IDS =================
def dls(start, goal, maze, limit, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    stack = [(start, [start], 0)]
    visited = set()
    while stack:
        (r,c), path, depth = stack.pop()
        if (r,c)==goal:
            return path
        if depth>=limit or (r,c) in visited:
            continue
        visited.add((r,c))
        if visualize:
            print_maze_step(maze, path, current=(r,c), start=start, goal=goal)
            time.sleep(delay)
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0:
                stack.append(((nr,nc), path+[(nr,nc)], depth+1))
    return None

def ids(start, goal, maze, max_depth=150, visualize=False, delay=0.05):
    for depth in range(max_depth+1):
        result = dls(start, goal, maze, depth, visualize=visualize, delay=delay)
        if result is not None:
            return result
    return []

# ================= Simulated Annealing =================
def simulated_annealing(start, goal, maze, visualize=False, delay=0.05, max_steps=1000, T=100.0, alpha=0.98):
    ROWS, COLS = len(maze), len(maze[0])
    current = start
    path = [current]

    for _ in range(max_steps):
        if current == goal:
            return path

        neighbors = [(current[0]+dr, current[1]+dc)
                     for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]
                     if 0 <= current[0]+dr < ROWS and 0 <= current[1]+dc < COLS and maze[current[0]+dr][current[1]+dc] == 0]

        if not neighbors:
            break

        nxt = random.choice(neighbors)
        deltaE = hx(current, goal) - hx(nxt, goal)
        if deltaE > 0 or random.random() < math.exp(deltaE / (T + 1e-5)):
            current = nxt
            path.append(current)
            if visualize:
                print_maze_step(maze, path, current=current, start=start, goal=goal)
                time.sleep(delay)
        T *= alpha

    return path

# ================= Genetic Algorithm =================
def genetic(start, goal, maze, pop_size=40, generations=100, mutation_rate=0.1, max_steps=80, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])

    def random_path():
        p, cur = [start], start
        for _ in range(max_steps):
            if cur == goal:
                break
            neighbors = [(cur[0]+dr, cur[1]+dc)
                         for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]
                         if 0 <= cur[0]+dr < ROWS and 0 <= cur[1]+dc < COLS and maze[cur[0]+dr][cur[1]+dc] == 0]
            if not neighbors:
                break
            cur = random.choice(neighbors)
            p.append(cur)
        return p

    def fitness(path):
        dist = hx(path[-1], goal)
        return 1 / (1 + dist + len(path) * 0.1)

    population = [random_path() for _ in range(pop_size)]

    for _ in range(generations):
        population.sort(key=lambda p: -fitness(p))
        best = population[0]
        if best[-1] == goal:
            if visualize:
                for step in best:
                    print_maze_step(maze, best, current=step, start=start, goal=goal)
                    time.sleep(delay)
            return best
        new_pop = population[:pop_size//2]
        while len(new_pop) < pop_size:
            p1, p2 = random.sample(population[:10], 2)
            cut = min(len(p1), len(p2)) // 2
            child = p1[:cut] + [s for s in p2 if s not in p1[:cut]]
            if random.random() < mutation_rate:
                child = random_path()
            new_pop.append(child)
        population = new_pop

    return population[0]

# ================= AC-3 (simplified) =================
def ac3(variables, domains, constraints):
    queue = [(xi,xj) for xi in variables for xj in variables if xi!=xj]
    while queue:
        xi,xj = queue.pop(0)
        revised = False
        for x in domains[xi][:]:
            if not any(constraints(xi,x,xj,y) for y in domains[xj]):
                domains[xi].remove(x)
                revised = True
        if revised:
            for xk in variables:
                if xk!=xi:
                    queue.append((xk,xi))
    return domains

# ================= AND-OR Graph Search (simplified) =================
def and_or_graph_search(problem):
    def or_search(state, path):
        if problem.goal_test(state):
            return []
        for action in problem.actions(state):
            result = and_search(problem.result(state, action), path+[state])
            if result is not None:
                return [action]+result
        return None
    def and_search(states, path):
        plan = []
        for s in states:
            result = or_search(s, path)
            if result is None:
                return None
            plan+=result
        return plan
    return or_search(problem.initial, [])

# ================= Minimax/Alpha-Beta =================
# ================= Minimax (Maze Version) =================
directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def hx(pos, goal):
    # Heuristic: Manhattan distance
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

def print_maze_step(maze, path=None, current=None, start=None, goal=None):
    if path is None:
        path = []
    display = ""
    for r in range(len(maze)):
        for c in range(len(maze[0])):
            if (r, c) == start:
                display += "S"
            elif (r, c) == goal:
                display += "G"
            elif (r, c) == current:
                display += "*"
            elif (r, c) in path:
                display += "o"
            elif maze[r][c] == 1:
                display += "#"
            else:
                display += "."
        display += "\n"
    print(display)

def minimax(node, goal, maze, depth, maximizing=True, visited=None, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    if visited is None:
        visited = set()

    def heuristic(pos):
        return -hx(pos, goal)

    if depth == 0 or node == goal:
        return heuristic(node), [node]

    visited.add(node)
    if visualize:
        print_maze_step(maze, [node], current=node, start=None, goal=goal)
        time.sleep(delay)

    best_path = [node]

    if maximizing:
        best_val = -math.inf
        for dr, dc in directions:
            nr, nc = node[0]+dr, node[1]+dc
            nxt = (nr, nc)
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and nxt not in visited:
                val, p = minimax(nxt, goal, maze, depth-1, False, visited.copy(), visualize, delay)
                if val > best_val:
                    best_val, best_path = val, [node] + p
    else:
        best_val = math.inf
        for dr, dc in directions:
            nr, nc = node[0]+dr, node[1]+dc
            nxt = (nr, nc)
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and nxt not in visited:
                val, p = minimax(nxt, goal, maze, depth-1, True, visited.copy(), visualize, delay)
                if val < best_val:
                    best_val, best_path = val, [node] + p
    return best_val, best_path

def minimax_maze(start, goal, maze, max_depth=5, visualize=False, delay=0.05):
    _, path = minimax(start, goal, maze, max_depth, True, set(), visualize, delay)
    return path if path else [start]


def alpha_beta(state, depth, alpha=-math.inf, beta=math.inf, maximize=True):
    if depth==0 or state.is_terminal():
        return state.utility(), None
    if maximize:
        best_move = None
        for move in state.get_moves():
            val,_ = alphabeta(state.make_move(move), depth-1, alpha, beta, False)
            if val>alpha:
                alpha = val
                best_move = move
            if alpha>=beta:
                break
        return alpha, best_move
    else:
        best_move = None
        for move in state.get_moves():
            val,_ = alphabeta(state.make_move(move), depth-1, alpha, beta, True)
            if val<beta:
                beta = val
                best_move = move
            if alpha>=beta:
                break
        return beta, best_move

# ================= POS (Partial Order Search) =================
def pos_search(actions, constraints):
    result = []
    available = set(actions)
    while available:
        for a in list(available):
            if all(pre in result for pre in constraints.get(a,[])):
                result.append(a)
                available.remove(a)
                break
    return result

# ================= Online DFS =================
def online_dfs(start, goal, maze, visualize=False, delay=0.05):
    ROWS,COLS = len(maze), len(maze[0])
    stack = [start]
    path = [start]
    visited = set()
    while stack:
        current = stack.pop()
        visited.add(current)
        if visualize:
            print_maze_step(maze, path, current=current, start=start, goal=goal)
            time.sleep(delay)
        if current==goal:
            return path
        for dr,dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr,nc = current[0]+dr, current[1]+dc
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0 and (nr,nc) not in visited:
                stack.append((nr,nc))
                path.append((nr,nc))
    return path
# ================= Minimax-Limited =================
def minimax_limited(start, goal, maze, max_depth=4, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def heuristic(pos):
        return -hx(pos, goal)

    def dfs_limited(node, depth, visited):
        if depth == 0 or node == goal:
            return heuristic(node), [node]
        visited.add(node)
        if visualize:
            print_maze_step(maze, [node], current=node, start=start, goal=goal)
            time.sleep(delay)
        best_val, best_path = -math.inf, [node]
        for dr, dc in directions:
            nr, nc = node[0]+dr, node[1]+dc
            nxt = (nr, nc)
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and nxt not in visited:
                val, p = dfs_limited(nxt, depth-1, visited.copy())
                if val > best_val:
                    best_val, best_path = val, [node] + p
        return best_val, best_path

    _, path = dfs_limited(start, max_depth, set())
    return path if path else [start]