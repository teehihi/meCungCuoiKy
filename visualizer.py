import time
from pathfinding import *

# ==============================
# Hiển thị mê cung
# ==============================
def print_maze(maze, path=None, current=None, start=None, goal=None):
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

# ==============================
# Wrapper để thêm visualizer
# ==============================
def visualize_algorithm(alg_func, maze, start, goal, delay=0.05, **kwargs):
    """
    alg_func: thuật toán từ pathfinding.py
    maze: ma trận 0/1
    start: (r,c)
    goal: (r,c)
    delay: thời gian sleep giữa các bước
    kwargs: tham số khác nếu thuật toán cần
    """
    path = []

    # Chúng ta tạo wrapper cho thuật toán để in từng bước
    # Với các thuật toán có vòng lặp chính => chỉnh sửa trong pathfinding
    # Cách đơn giản: thuật toán trả về path cuối, hiển thị animation final path
    print(f"Running {alg_func.__name__}...")
    path = alg_func(start, goal, maze, **kwargs)
    
    # In final path
    print("Final Path:")
    print_maze(maze, path=path, start=start, goal=goal)
    return path

# ==============================
# Test tất cả thuật toán
# ==============================
def test_all_algorithms(maze, start, goal):
    algorithms = [
        bfs, dfs, ids, astar, greedy, ucs,
        hill_climbing, simulated_annealing,
        genetic, backtracking, forwardchecking, ac3,
        online_dfs, pos, and_or_tree_search
    ]
    
    for alg in algorithms:
        input(f"\nPress Enter to run {alg.__name__}...")
        path = visualize_algorithm(alg, maze, start, goal, delay=0.05)
        print(f"Path length: {len(path)}")

# ==============================
# Example usage
# ==============================

