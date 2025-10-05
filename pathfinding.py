from collections import deque
import heapq
import random
import math

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


# AND-OR Tree Search
def and_or_tree_search(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])

    def successors(state):
        r, c = state
        next_states = []
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                next_states.append((nr, nc))
        return next_states

    # Hàm đệ quy giải quyết node OR
    def or_search(state, path):
        if state == goal:
            return path
        if state in path:  # tránh vòng lặp
            return None
        for s in successors(state):
            plan = and_search(s, path+[s])
            if plan is not None:
                return plan
        return None

    # Hàm đệ quy giải quyết node AND
    def and_search(state, path):
        return or_search(state, path)

    # Bắt đầu từ start
    return or_search(start, [start]) or []


# Online DFS Search trong không gian không nhìn thấy
def online_dfs(start, goal, maze, max_steps=1000):
    ROWS, COLS = len(maze), len(maze[0])

    # Trạng thái hiện tại
    current = start
    path = [current]

    # Đã khám phá được các cạnh từ mỗi state
    unexplored = {}
    visited = set()

    for _ in range(max_steps):
        if current == goal:
            return path

        # Nếu chưa khám phá neighbors thì khám phá
        if current not in unexplored:
            r, c = current
            neighbors = []
            for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                    neighbors.append((nr,nc))
            unexplored[current] = neighbors

        # Nếu còn neighbor chưa thăm → đi tiếp
        if unexplored[current]:
            next_state = unexplored[current].pop()
            if next_state not in visited:
                current = next_state
                path.append(current)
                visited.add(current)
                continue

        # Nếu không còn neighbor nào → quay lui
        if len(path) > 1:
            path.pop()
            current = path[-1]
        else:
            break

    return path if current == goal else []


# Partially Observable Search (POS) - tìm kiếm trong không gian nhìn thấy một phần
def pos(start, goal, maze, max_steps=2000):
    ROWS, COLS = len(maze), len(maze[0])

    # Bản đồ mà agent biết (khởi tạo: chỉ biết start)
    known = {start: 0}
    frontier = [(start, [start])]
    visited = set()

    step_count = 0
    while frontier and step_count < max_steps:
        state, path = frontier.pop(0)
        step_count += 1

        if state == goal:
            return path

        if state in visited:
            continue
        visited.add(state)

        r, c = state

        # Agent "nhìn thấy" các ô xung quanh (tầm nhìn = 1)
        visible_neighbors = []
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if maze[nr][nc] == 0:  # đi được
                    known[(nr,nc)] = 0
                    visible_neighbors.append((nr,nc))

        # Thêm vào frontier để khám phá tiếp
        for n in visible_neighbors:
            if n not in visited:
                frontier.append((n, path+[n]))

    return []  # nếu không tìm thấy trong max_steps

# Backtracking Search
def backtracking(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    path = []
    visited = set()

    def bt(r, c):
        if (r, c) == goal:
            path.append((r, c))
            return True
        if (r, c) in visited:
            return False
        visited.add((r, c))
        path.append((r, c))

        # Thử đi 4 hướng
        for dr, dc in [(1,0), (0,1), (-1,0), (0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                if bt(nr, nc):
                    return True

        # Nếu không thành công → quay lui
        path.pop()
        return False

    if bt(start[0], start[1]):
        return path
    else:
        return []

# Forward Checking Search (áp dụng cho mê cung như CSP đơn giản)
def forwardchecking(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])
    path = []
    visited = set()

    # Hàm kiểm tra domain của 1 ô (có neighbor hợp lệ không)
    def domain_ok(r, c):
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr, nc) not in visited:
                return True
        return False

    def fc(r, c):
        if (r, c) == goal:
            path.append((r, c))
            return True
        if (r, c) in visited:
            return False
        visited.add((r, c))
        path.append((r, c))

        # Thử các neighbor nhưng chỉ đi nếu domain còn hợp lệ
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr, nc) not in visited:
                if domain_ok(nr, nc):  # forward checking
                    if fc(nr, nc):
                        return True

        # Quay lui
        path.pop()
        return False

    if fc(start[0], start[1]):
        return path
    else:
        return []

# AC-3 (Arc Consistency)
def ac3(start, goal, maze):
    ROWS, COLS = len(maze), len(maze[0])

    # Domain: mỗi node có domain {0} (đi được) hoặc rỗng nếu tường
    domains = {}
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == 0:
                domains[(r,c)] = {0}  # đi được
            else:
                domains[(r,c)] = set()  # không đi được

    # Constraint: một node và neighbor đều phải có domain khác rỗng
    def neighbors(r,c):
        for dr, dc in [(1,0),(0,1),(-1,0),(0,-1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                yield (nr,nc)

    # Arc ban đầu: tất cả cặp (X,Y) với Y là neighbor của X
    queue = deque()
    for r in range(ROWS):
        for c in range(COLS):
            for n in neighbors(r,c):
                queue.append(((r,c), n))

    # Revise: loại giá trị khỏi domain[x] nếu không còn giá trị nào ở domain[y] hỗ trợ nó
    def revise(x, y):
        removed = False
        if not domains[y]:  # nếu domain y rỗng thì x cũng không còn hợp lệ
            if domains[x]:
                domains[x].clear()
                removed = True
        return removed

    # AC-3 main loop
    while queue:
        (x, y) = queue.popleft()
        if revise(x, y):
            if not domains[x]:
                continue
            for n in neighbors(*x):
                if n != y:
                    queue.append((n, x))

    # Sau khi AC-3, nếu start hoặc goal rỗng domain => không có đường
    if not domains.get(start, set()) or not domains.get(goal, set()):
        return []

    # Nếu còn hợp lệ → chạy BFS/A* để tìm đường đi
    return bfs(start, goal, maze)


# Minimax Search (Thuật toán Minimax cơ bản)
def minimax(state, depth, maximizing_player, get_children, evaluate, is_terminal):
    # Nếu đạt độ sâu giới hạn hoặc node là terminal → trả về giá trị heuristic
    if depth == 0 or is_terminal(state):
        return evaluate(state)

    # Lượt của MAX → chọn giá trị lớn nhất
    if maximizing_player:
        max_eval = float('-inf')
        for child in get_children(state):
            eval = minimax(child, depth - 1, False, get_children, evaluate, is_terminal)
            max_eval = max(max_eval, eval)
        return max_eval

    # Lượt của MIN → chọn giá trị nhỏ nhất
    else:
        min_eval = float('inf')
        for child in get_children(state):
            eval = minimax(child, depth - 1, True, get_children, evaluate, is_terminal)
            min_eval = min(min_eval, eval)
        return min_eval


# Alpha-Beta Pruning (Thuật toán Cắt tỉa Alpha–Beta)
def alphabeta(state, depth, alpha, beta, maximizing_player, get_children, evaluate, is_terminal):
    # Nếu đạt độ sâu giới hạn hoặc node là terminal → trả về giá trị heuristic
    if depth == 0 or is_terminal(state):
        return evaluate(state)

    # Lượt của MAX → cố gắng tăng alpha
    if maximizing_player:
        max_eval = float('-inf')
        for child in get_children(state):
            eval = alphabeta(child, depth - 1, alpha, beta, False, get_children, evaluate, is_terminal)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Cắt tỉa (prune)
        return max_eval

    # Lượt của MIN → cố gắng giảm beta
    else:
        min_eval = float('inf')
        for child in get_children(state):
            eval = alphabeta(child, depth - 1, alpha, beta, True, get_children, evaluate, is_terminal)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Cắt tỉa (prune)
        return min_eval

# Biến thể của minimax - Giới hạn độ sâu ( để tránh lặp vô hạn) 
def minimax_limited(state, depth, maximizing_player, get_children, evaluate, is_terminal):
    if depth == 0 or is_terminal(state):
        return evaluate(state)
    if maximizing_player:
        max_eval = float('-inf')
        for child in get_children(state):
            eval = minimax_limited(child, depth - 1, False, get_children, evaluate, is_terminal)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for child in get_children(state):
            eval = minimax_limited(child, depth - 1, True, get_children, evaluate, is_terminal)
            min_eval = min(min_eval, eval)
        return min_eval
