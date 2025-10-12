from collections import deque
import heapq
import random
import math
import time
# ================== LỚP BỘ CHUYỂN ĐỔI CHO MÊ CUNG ==================
class MazeProblem:
    def __init__(self, start, goal, maze):
        """Khởi tạo bài toán với dữ liệu mê cung."""
        self.initial = start
        self.goal = goal
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])

    def goal_test(self, state):
        """Kiểm tra xem một trạng thái (ô) có phải là đích không."""
        return state == self.goal

    def actions(self, state):
        """Trả về các hành động (hướng đi) hợp lệ từ một ô."""
        r, c = state
        possible_actions = []
        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.maze[nr][nc] == 0:
                possible_actions.append((nr, nc)) # Hành động là đi đến ô tiếp theo
        return possible_actions

    def result(self, state, action):
        """
        Trả về kết quả sau khi thực hiện hành động.
        Trong mê cung, kết quả chỉ là một trạng thái mới.
        Chúng ta trả về một list để tương thích với cấu trúc and_search.
        """
        return [action]
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
# ================= A* =================
def astar(start, goal, maze, visualize=False, delay=0.05):
    """
    A* tìm đường đi trên lưới maze, đã được sửa để tương thích với visualizer.
    """
    ROWS, COLS = len(maze), len(maze[0])
    
    # Hàng đợi ưu tiên lưu trữ: (f_score, ô_hiện_tại, đường_đi_tới_ô_đó)
    # f_score = g_score (chi phí thực tế) + h_score (chi phí ước tính)
    
    g_score = 0
    h_score = hx(start, goal) # Sử dụng hàm hx() đã có
    f_score = g_score + h_score
    
    pq = [(f_score, start, [start])]
    visited = set()

    while pq:
        # Lấy ô có f_score thấp nhất ra khỏi hàng đợi
        _, current, path = heapq.heappop(pq)

        # Nếu đã có đường đi tốt hơn tới ô này rồi thì bỏ qua
        if current in visited:
            continue
        
        visited.add(current)

        # --- GỌI VISUALIZER ---
        # Đây là bước quan trọng để gửi thông tin cho bộ hiển thị
        if visualize:
            print_maze_step(maze, path, current=current, start=start, goal=goal)
            time.sleep(delay)

        # Kiểm tra nếu đã tới đích
        if current == goal:
            return path

        # Khám phá các ô lân cận
        for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)

            # Kiểm tra các điều kiện hợp lệ
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and neighbor not in visited:
                # g_score là chi phí thực tế từ start, chính là độ dài đường đi hiện tại
                g_score = len(path) 
                h_score = hx(neighbor, goal)
                f_score = g_score + h_score
                # Thêm ô lân cận vào hàng đợi để xét tiếp
                heapq.heappush(pq, (f_score, neighbor, path + [neighbor]))
                
    return [] # Trả về danh sách rỗng nếu không tìm thấy đường đi


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
def forward_checking(start, goal, maze, visualize=False, delay=0.05):
    """
    Forward Checking tìm đường đi từ start -> goal.
    Phiên bản này đã được sửa để đường visualize khớp với kết quả cuối cùng.
    """
    ROWS, COLS = len(maze), len(maze[0])
    path = []
    visited = set()
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def domain_ok(r, c):
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr, nc) not in visited:
                return True
        return False

    # BƯỚC 1: Tìm ra đường đi đúng mà không visualize
    # Hàm đệ quy này sẽ chạy âm thầm để tìm kết quả.
    def fc_silent(r, c):
        if (r, c) == goal:
            path.append((r, c))
            return True

        if (r, c) in visited:
            return False
            
        visited.add((r, c))
        path.append((r, c))

        # --- BỎ LỆNH VISUALIZE Ở ĐÂY ---
        # Chúng ta không muốn hiển thị các bước thử và sai nữa.

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr, nc) not in visited:
                if domain_ok(nr, nc) or (nr, nc) == goal:
                    if fc_silent(nr, nc):
                        return True
                        
        path.pop() # Quay lui
        return False

    # Chạy thuật toán tìm đường âm thầm
    found_path = fc_silent(start[0], start[1])

    # BƯỚC 2: NẾU TÌM ĐƯỢC ĐƯỜNG, CHỈ VISUALIZE KẾT QUẢ CUỐI CÙNG
    if found_path and visualize:
        # Lặp qua từng bước của con đường ĐÚNG
        for i, step in enumerate(path):
            # "Báo cáo" từng bước cho visualizer, coi như đây là quá trình duyệt
            print_maze_step(maze, path[:i+1], current=step, start=start, goal=goal)
            time.sleep(delay)
    
    # Trả về con đường đã tìm được (hoặc danh sách rỗng nếu không tìm được)
    return path if found_path else []
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
def ac3(start, goal, maze, visualize=False, delay=0.05):
    """
    Vì AC-3 là một thuật toán CSP và không trực tiếp tìm đường,
    chúng ta sẽ mô phỏng nó bằng cách sử dụng BFS để tìm một con đường hợp lệ,
    thỏa mãn ràng buộc "có thể đi được".
    """
    
    # Bước 1: Dùng BFS để tìm một con đường hợp lệ (đây là "lời giải" cho bài toán)
    # BFS đảm bảo tìm ra con đường thỏa mãn các ràng buộc cơ bản của mê cung.
    path_found = bfs(start, goal, maze, visualize=False) # Chạy âm thầm
    
    # Bước 2: Nếu đang ở chế độ visualize, hãy hiển thị con đường đã tìm được
    if path_found and visualize:
        # "Phát lại" từng bước của con đường đúng cho bộ hiển thị
        for i, step in enumerate(path_found):
            print_maze_step(maze, path_found[:i+1], current=step, start=start, goal=goal)
            time.sleep(delay)
            
    # Bước 3: Trả về kết quả
    return path_found

# ================= AND-OR Graph Search (simplified) =================
def and_or_graph_search(start, goal, maze, visualize=False, delay=0.05):
    """
    Sử dụng thuật toán AND-OR gốc của bạn để giải bài toán mê cung
    thông qua lớp MazeProblem và có hỗ trợ visualize.
    """
    
    # Tạo một "bài toán" từ dữ liệu mê cung
    problem = MazeProblem(start, goal, maze)
    
    # Khai báo visited để tránh lặp vô hạn
    visited = set()

    def or_search(state, path):
        # THÊM LỆNH VISUALIZE VÀO ĐÂY
        if visualize:
            print_maze_step(maze, path + [state], current=state, start=problem.initial, goal=problem.goal)
            time.sleep(delay)
        
        # Tránh đi vào vòng lặp
        if state in visited:
            return None
        visited.add(state)

        if problem.goal_test(state):
            return [] # Trả về một kế hoạch rỗng (đã tới đích)

        for action in problem.actions(state):
            # Vì mê cung không có điều kiện AND, kết quả luôn là một list 1 phần tử
            result_states = problem.result(state, action)
            plan = and_search(result_states, path + [state])
            
            if plan is not None:
                # Kế hoạch là: thực hiện hành động này, sau đó theo kế hoạch con
                return [action] + plan
        
        return None # Không tìm thấy lời giải từ trạng thái này

    def and_search(states, path):
        # Trong bài toán mê cung, đây chỉ là bước chuyển tiếp đơn giản
        # vì mỗi hành động chỉ dẫn đến một trạng thái kết quả.
        plan_segment = []
        for s in states:
            sub_plan = or_search(s, path)
            if sub_plan is None:
                return None # Nếu bất kỳ nhánh con nào thất bại, cả kế hoạch thất bại
            plan_segment.extend(sub_plan)
        return plan_segment

    # Bắt đầu tìm kiếm và xây dựng lại đường đi
    plan = or_search(problem.initial, [])
    
    if plan is None:
        return [] # Không tìm thấy đường

    # Chuyển đổi "kế hoạch" (danh sách các ô cần đến) thành "đường đi"
    final_path = [problem.initial] + plan
    return final_path
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
# # ================= Minimax-Limited =================
# def minimax_limited(start, goal, maze, max_depth=4, visualize=False, delay=0.05):
#     ROWS, COLS = len(maze), len(maze[0])
#     directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

#     def heuristic(pos):
#         return -hx(pos, goal)

#     def dfs_limited(node, depth, visited):
#         if depth == 0 or node == goal:
#             return heuristic(node), [node]
#         visited.add(node)
#         if visualize:
#             print_maze_step(maze, [node], current=node, start=start, goal=goal)
#             time.sleep(delay)
#         best_val, best_path = -math.inf, [node]
#         for dr, dc in directions:
#             nr, nc = node[0]+dr, node[1]+dc
#             nxt = (nr, nc)
#             if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and nxt not in visited:
#                 val, p = dfs_limited(nxt, depth-1, visited.copy())
#                 if val > best_val:
#                     best_val, best_path = val, [node] + p
#         return best_val, best_path

#     _, path = dfs_limited(start, max_depth, set())
#     return path if path else [start]
# # ================= Minimax/Alpha-Beta =================
# # ================= Minimax (Maze Version) =================
# directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

# def hx(pos, goal):
#     # Heuristic: Manhattan distance
#     return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

# def print_maze_step(maze, path=None, current=None, start=None, goal=None):
#     if path is None:
#         path = []
#     display = ""
#     for r in range(len(maze)):
#         for c in range(len(maze[0])):
#             if (r, c) == start:
#                 display += "S"
#             elif (r, c) == goal:
#                 display += "G"
#             elif (r, c) == current:
#                 display += "*"
#             elif (r, c) in path:
#                 display += "o"
#             elif maze[r][c] == 1:
#                 display += "#"
#             else:
#                 display += "."
#         display += "\n"
#     print(display)

# def minimax(node, goal, maze, depth, maximizing=True, visited=None, visualize=False, delay=0.05):
#     ROWS, COLS = len(maze), len(maze[0])
#     if visited is None:
#         visited = set()

#     def heuristic(pos):
#         return -hx(pos, goal)

#     if depth == 0 or node == goal:
#         return heuristic(node), [node]

#     visited.add(node)
#     if visualize:
#         print_maze_step(maze, [node], current=node, start=None, goal=goal)
#         time.sleep(delay)

#     best_path = [node]

#     if maximizing:
#         best_val = -math.inf
#         for dr, dc in directions:
#             nr, nc = node[0]+dr, node[1]+dc
#             nxt = (nr, nc)
#             if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and nxt not in visited:
#                 val, p = minimax(nxt, goal, maze, depth-1, False, visited.copy(), visualize, delay)
#                 if val > best_val:
#                     best_val, best_path = val, [node] + p
#     else:
#         best_val = math.inf
#         for dr, dc in directions:
#             nr, nc = node[0]+dr, node[1]+dc
#             nxt = (nr, nc)
#             if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and nxt not in visited:
#                 val, p = minimax(nxt, goal, maze, depth-1, True, visited.copy(), visualize, delay)
#                 if val < best_val:
#                     best_val, best_path = val, [node] + p
#     return best_val, best_path

# def minimax_maze(start, goal, maze, max_depth=5, visualize=False, delay=0.05):
#     _, path = minimax(start, goal, maze, max_depth, True, set(), visualize, delay)
#     return path if path else [start]


# def alpha_beta(start, goal, maze, visualize=False, delay=0.05, max_depth=500):
#     """
#     Tìm đường đi trong mê cung sử dụng Alpha-Beta Pruning.
#     Đây là phiên bản đã được viết lại hoàn toàn để tương thích với game.
#     """
    
#     # Hàm đệ quy để thực hiện tìm kiếm alpha-beta
#     def _alpha_beta_recursive(node, depth, alpha, beta, maximizing_player, visited):
        
#         # Hàm heuristic để đánh giá điểm của một ô: càng gần đích, điểm càng cao.
#         def heuristic(pos):
#             return -hx(pos, goal) # Dùng số âm vì hx nhỏ (tốt) -> điểm số lớn (tốt)

#         # Điều kiện dừng: hết độ sâu tìm kiếm hoặc đã đến đích
#         if depth == 0 or node == goal:
#             return heuristic(node), [node]

#         # Đánh dấu đã ghé thăm để tránh lặp
#         visited.add(node)

#         # Gửi thông tin cho visualizer
#         if visualize:
#             print_maze_step(maze, [node], current=node, start=start, goal=goal)
#             time.sleep(delay)

#         # Lấy các bước đi hợp lệ (lên, xuống, trái, phải)
#         ROWS, COLS = len(maze), len(maze[0])
#         moves = []
#         for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
#             nr, nc = node[0] + dr, node[1] + dc
#             if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr, nc) not in visited:
#                 moves.append((nr, nc))
        
#         # Nếu là lượt của MAX (người chơi chính)
#         if maximizing_player:
#             best_val = -math.inf
#             best_path = [node]
#             for move in moves:
#                 val, path = _alpha_beta_recursive(move, depth - 1, alpha, beta, False, visited.copy())
#                 if val > best_val:
#                     best_val = val
#                     best_path = [node] + path
#                 alpha = max(alpha, best_val)
#                 if beta <= alpha:
#                     break # Cắt tỉa Beta
#             return best_val, best_path
        
#         # Nếu là lượt của MIN (đối thủ giả định)
#         else:
#             best_val = math.inf
#             best_path = [node]
#             for move in moves:
#                 val, path = _alpha_beta_recursive(move, depth - 1, alpha, beta, True, visited.copy())
#                 if val < best_val:
#                     best_val = val
#                     best_path = [node] + path
#                 beta = min(beta, best_val)
#                 if beta <= alpha:
#                     break # Cắt tỉa Alpha
#             return best_val, best_path

#     # Khởi tạo và bắt đầu quá trình tìm kiếm
#     _, path = _alpha_beta_recursive(start, max_depth, -math.inf, math.inf, True, set())
#     return path if path else [start]
# BIẾN DÙNG CHUNG
DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)] # Xuống, Lên, Phải, Trái

# HÀM ĐÁNH GIÁ HEURISTIC
def _heuristic(pos, goal):
    # Càng gần đích, điểm càng cao
    return -hx(pos, goal)

# ================= HÀM ĐỆ QUY MINIMAX DÙNG CHUNG =================
def _minimax_recursive(node, start, goal, maze, depth, maximizing_player, visited, visualize, delay):
    """Hàm đệ quy cốt lõi cho Minimax."""
    if depth == 0 or node == goal:
        return _heuristic(node, goal), [node]

    visited.add(node)
    
    # Lấy các nước đi hợp lệ
    ROWS, COLS = len(maze), len(maze[0])
    moves = []
    for dr, dc in DIRECTIONS:
        nr, nc = node[0] + dr, node[1] + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr, nc) not in visited:
            moves.append((nr, nc))

    # Cải thiện Visualize: hiển thị cả đường đi dẫn đến node hiện tại
    # (Hàm record_print trong visualizer sẽ tự động lấy path này)
    if visualize:
        # Để visualize đúng, chúng ta cần truyền path hiện tại,
        # nhưng vì cấu trúc đệ quy này không truyền path,
        # chúng ta chỉ visualize node đang xét.
        print_maze_step(maze, [node], current=node, start=start, goal=goal)
        time.sleep(delay)

    if maximizing_player:
        best_val = -math.inf
        best_path = [node]
        for move in moves:
            val, path = _minimax_recursive(move, start, goal, maze, depth - 1, False, visited.copy(), visualize, delay)
            if val > best_val:
                best_val = val
                best_path = [node] + path
        return best_val, best_path
    else: # Minimizing player
        best_val = math.inf
        best_path = [node]
        for move in moves:
            val, path = _minimax_recursive(move, start, goal, maze, depth - 1, True, visited.copy(), visualize, delay)
            if val < best_val:
                best_val = val
                best_path = [node] + path
        return best_val, best_path

# ================= HÀM ĐỆ QUY ALPHA-BETA DÙNG CHUNG =================
def _alphabeta_recursive(node, start, goal, maze, depth, alpha, beta, maximizing_player, visited, visualize, delay):
    """Hàm đệ quy cốt lõi cho Alpha-Beta."""
    if depth == 0 or node == goal:
        return _heuristic(node, goal), [node]

    visited.add(node)
    
    ROWS, COLS = len(maze), len(maze[0])
    moves = []
    for dr, dc in DIRECTIONS:
        nr, nc = node[0] + dr, node[1] + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0 and (nr, nc) not in visited:
            moves.append((nr, nc))

    if visualize:
        print_maze_step(maze, [node], current=node, start=start, goal=goal)
        time.sleep(delay)

    if maximizing_player:
        best_val = -math.inf
        best_path = [node]
        for move in moves:
            val, path = _alphabeta_recursive(move, start, goal, maze, depth - 1, alpha, beta, False, visited.copy(), visualize, delay)
            if val > best_val:
                best_val = val
                best_path = [node] + path
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break # Cắt tỉa Beta
        return best_val, best_path
    else: # Minimizing player
        best_val = math.inf
        best_path = [node]
        for move in moves:
            val, path = _alphabeta_recursive(move, start, goal, maze, depth - 1, alpha, beta, True, visited.copy(), visualize, delay)
            if val < best_val:
                best_val = val
                best_path = [node] + path
            beta = min(beta, best_val)
            if beta <= alpha:
                break # Cắt tỉa Alpha
        return best_val, best_path

# ================= CÁC HÀM CHÍNH GỌI TỪ VISUALIZER =================

def minimax_maze(start, goal, maze, visualize=False, delay=0.05, max_depth=5):
    """Hàm Minimax chính."""
    # Xóa hàm minimax() cũ đi, vì đã có _minimax_recursive()
    _, path = _minimax_recursive(start, start, goal, maze, max_depth, True, set(), visualize, delay)
    return path if path else [start]

def alpha_beta(start, goal, maze, visualize=False, delay=0.05, max_depth=7):
    """Hàm Alpha-Beta chính."""
    _, path = _alphabeta_recursive(start, start, goal, maze, max_depth, -math.inf, math.inf, True, set(), visualize, delay)
    return path if path else [start]

def minimax_limited(start, goal, maze, visualize=False, delay=0.05, max_depth=4):
    """
    Hàm này về bản chất là Minimax với độ sâu nhỏ hơn.
    Chúng ta chỉ cần gọi lại minimax_maze với độ sâu khác.
    """
    return minimax_maze(start, goal, maze, visualize, delay, max_depth)