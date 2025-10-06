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
def astar(start, goal, maze, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    pq = [(hx(start, goal), 0, start, [start])]
    visited = set()
    while pq:
        f, g, (r,c), path = heapq.heappop(pq)
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
                g2 = g+1
                f2 = g2 + hx((nr,nc), goal)
                heapq.heappush(pq, (f2, g2, (nr,nc), path+[(nr,nc)]))
    return []

# ================= Hill Climbing =================
def hill_climbing(start, goal, maze, visualize=False, delay=0.05, max_steps=1000):
    ROWS, COLS = len(maze), len(maze[0])
    current = start
    path = [current]
    for _ in range(max_steps):
        if current == goal:
            return path
        neighbors = [(current[0]+dr, current[1]+dc) for dr,dc in [(1,0),(0,1),(-1,0),(0,-1)]
                     if 0<=current[0]+dr<ROWS and 0<=current[1]+dc<COLS and maze[current[0]+dr][current[1]+dc]==0]
        if not neighbors:
            break
        best = min(neighbors, key=lambda x:hx(x, goal))
        if hx(best, goal) >= hx(current, goal):
            break
        current = best
        path.append(current)
        if visualize:
            print_maze_step(maze, path, current=current, start=start, goal=goal)
            time.sleep(delay)
    return path if current==goal else []

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
def forwardchecking(start, goal, maze, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    path = []
    visited = set()
    def domain_ok(r,c):
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0 and (nr,nc) not in visited:
                return True
        return False
    def fc(r,c):
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
            if 0<=nr<ROWS and 0<=nc<COLS and maze[nr][nc]==0 and (nr,nc) not in visited:
                if domain_ok(nr,nc):
                    if fc(nr,nc):
                        return True
        path.pop()
        return False
    if fc(start[0], start[1]):
        return path
    return []

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

def ids(start, goal, maze, max_depth=50, visualize=False, delay=0.05):
    for depth in range(max_depth+1):
        result = dls(start, goal, maze, depth, visualize=visualize, delay=delay)
        if result is not None:
            return result
    return []

# ================= Simulated Annealing =================
def simulated_annealing(start, goal, maze, visualize=False, delay=0.05, max_steps=1000, T=100.0, alpha=0.99):
    ROWS, COLS = len(maze), len(maze[0])
    current = start
    path = [current]
    for _ in range(max_steps):
        if current==goal:
            return path
        neighbors = [(current[0]+dr, current[1]+dc) for dr,dc in [(1,0),(0,1),(-1,0),(0,-1)]
                     if 0<=current[0]+dr<ROWS and 0<=current[1]+dc<COLS and maze[current[0]+dr][current[1]+dc]==0]
        if not neighbors:
            break
        next_node = random.choice(neighbors)
        deltaE = hx(current, goal)-hx(next_node, goal)
        if deltaE>0 or random.random() < math.exp(deltaE/T if T>0 else 0):
            current = next_node
            path.append(current)
            if visualize:
                print_maze_step(maze, path, current=current, start=start, goal=goal)
                time.sleep(delay)
        T *= alpha
    return path if current==goal else []

# ================= Genetic Algorithm =================
def genetic(start, goal, maze, pop_size=50, generations=200, mutation_rate=0.1, max_steps=100, visualize=False, delay=0.05):
    ROWS, COLS = len(maze), len(maze[0])
    def random_path():
        path = [start]
        current = start
        for _ in range(max_steps):
            if current == goal:
                break
            neighbors = [(current[0]+dr,current[1]+dc) for dr,dc in [(1,0),(0,1),(-1,0),(0,-1)]
                         if 0<=current[0]+dr<ROWS and 0<=current[1]+dc<COLS and maze[current[0]+dr][current[1]+dc]==0]
            if not neighbors:
                break
            current = random.choice(neighbors)
            path.append(current)
        return path
    def fitness(path):
        last = path[-1]
        dist = abs(last[0]-goal[0])+abs(last[1]-goal[1])
        return 1/(dist+1+len(path)*0.01)
    def crossover(p1,p2):
        cut = min(len(p1),len(p2))//2
        child = p1[:cut]
        for step in p2:
            if step not in child:
                child.append(step)
        return child
    def mutate(path):
        if len(path)<=2:
            return path
        if random.random()<mutation_rate:
            idx = random.randint(1,len(path)-1)
            path = path[:idx]
            current = path[-1]
            for _ in range(max_steps-idx):
                if current==goal:
                    break
                neighbors = [(current[0]+dr,current[1]+dc) for dr,dc in [(1,0),(0,1),(-1,0),(0,-1)]
                             if 0<=current[0]+dr<ROWS and 0<=current[1]+dc<COLS and maze[current[0]+dr][current[1]+dc]==0]
                if not neighbors:
                    break
                current = random.choice(neighbors)
                path.append(current)
        return path
    population = [random_path() for _ in range(pop_size)]
    for _ in range(generations):
        population.sort(key=lambda x:-fitness(x))
        if population[0][-1]==goal:
            if visualize:
                for step in population[0]:
                    print_maze_step(maze, path=population[0], current=step, start=start, goal=goal)
                    time.sleep(delay)
            return population[0]
        next_gen = population[:pop_size//2]
        while len(next_gen)<pop_size:
            p1,p2 = random.sample(population[:10],2)
            child = mutate(crossover(p1,p2))
            next_gen.append(child)
        population = next_gen
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
def minimax(state, depth, maximize=True):
    if depth==0 or state.is_terminal():
        return state.utility(), None
    if maximize:
        best_val = -math.inf
        best_move = None
        for move in state.get_moves():
            val,_ = minimax(state.make_move(move), depth-1, False)
            if val>best_val:
                best_val = val
                best_move = move
        return best_val, best_move
    else:
        best_val = math.inf
        best_move = None
        for move in state.get_moves():
            val,_ = minimax(state.make_move(move), depth-1, True)
            if val<best_val:
                best_val = val
                best_move = move
        return best_val, best_move

def alphabeta(state, depth, alpha=-math.inf, beta=math.inf, maximize=True):
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
