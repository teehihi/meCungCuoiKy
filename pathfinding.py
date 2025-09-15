from collections import deque

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
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] == 0:
                if (nr, nc) not in visited:
                    stack.append(((nr, nc), path + [(nr, nc)]))

    return []
