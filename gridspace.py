import numpy as np
import serial
import time
import math


class Gridspace:
    def __init__(self, grid=None):
        if grid is None:
            self.grid = None
            self.rows = None
            self.cols = None
        else:
            self.grid = np.array(grid, dtype=int)
            self.rows = len(self.grid)
            self.cols = len(self.grid[0])
        self.current = {'x' : 0, 'y' : 0}
        self.previous = {'x' : 0, 'y' : 0}
        self.label = {'unexplored' : 0, 'current': 1, 'person' : 2, 'path': 3, 'explored' : 4, 'obstacle': 7, 'destination a': 8, 'destination b': 9}
        self.gridsize = 0.5

    def initialize_grid(self, x_size, y_size):
        """Initialize the grid based on provided x and y sizes."""
        # Each grid cell represents a self.gridsize meters x self.gridsize meters area.
        self.grid = np.zeros((math.ceil(y_size / self.gridsize), math.ceil(x_size / self.gridsize)), dtype=int)
        self.rows = len(self.grid)
        self.cols= len(self.grid[0])
        print(f"Grid initialized with dimensions: {self.grid.shape[0]}x{self.grid.shape[1]}")

    def update_grid(self, label_name, x, y):
        if label_name in self.label:
            label_value = self.label[label_name]
            if 0 <= x < self.cols and 0 <= y < self.rows:
                # Update the grid if within bounds and label exists
                self.grid[y, x] = label_value
                #print(f"Grid updated at ({x}, {y}) with label '{label_name}' ({label_value}).\n")
            else:
                # Handle out-of-bounds coordinates
                print(f"Error: Coordinates ({x}, {y}) are out of grid bounds.")
        else:
            # Handle undefined label
            print(f"Error: Label '{label_name}' is not defined.")

    def update_position(self, label, x, y):
        # Assuming bottom left corner is (0,0) and measurements in meters.
        if self.grid is not None and x >= 0 and y >= 0:
            grid_x = math.ceil(x / self.gridsize)
            grid_y = math.ceil(y / self.gridsize)
            self.current = {'x': grid_x, 'y': grid_y}
            if 0 <= grid_x < self.grid.shape[1] and 0 <= grid_y < self.grid.shape[0]:
                # Only update if the current position has changed from the previous position
                if self.previous and (self.previous != self.current):
                    # If previous position was labeled as our current position and it's no longer current, change to explored
                    if self.grid[self.previous['y'], self.previous['x']] == self.label['current']:
                        self.grid[self.previous['y'], self.previous['x']] = self.label['explored']
                # Update the grid with the new label
                self.grid[grid_y, grid_x] = label
                # Store the current position as previous for the next update
                self.previous = {'x': grid_x, 'y': grid_y}
            else:
                print(f"Attempted to update position out of grid bounds: ({x}, {y})")
        else:
            print("Grid has not been initialized\n.")

    def get_grid_position(self):
        return (self.current['x'], self.current['y'])
        

    def display_grid(self):
        """
        Prints the grid to the console. Each row is displayed as a continuous string of numbers,
        each followed by a newline character.
        """
        if self.grid is not None:
            for row in self.grid:
                print(''.join(map(str, row)) + '\n', end='')
        else:
            print("Grid has not been initialized.\n", end='')
        print()

    def display_grid2(self):
        for row in self.grid:
            print(row)

    def get_neighbors(self, node):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        (x, y) = node
        neighbors = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols:
                if self.grid[nx][ny] != self.label['obstacle']:
                    neighbors.append((nx, ny))
        return neighbors

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    def astar(self, start, destination_value):
        # Find the destination node
        destination = None
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == destination_value:
                    destination = (r, c)
                    break
            if destination:
                break

        if not destination:
            return None

        open_set = []
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, destination)}
        open_set.append((f_score[start], start))

        while open_set:
            current = min(open_set, key=lambda x: x[0])[1]
            if current == destination:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(current)
                return path[::-1]

            open_set = [x for x in open_set if x[1] != current]
            for neighbor in self.get_neighbors(current):
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, destination)
                    if (f_score[neighbor], neighbor) not in open_set:
                        open_set.append((f_score[neighbor], neighbor))
        return None

    def find_path(self, start, destination):
        print("pathing")
        path = self.astar(start, destination)
        if path:
            print("Path found:", path)
            for i in range(len(self.grid)):
                for j in range(len(self.grid[i])):
                    if self.grid[i][j] == self.label['path']:
                        self.grid[i][j] = self.label['explored']
            for (x, y) in path:
                if (x, y) != start and self.grid[x][y] != destination:
                    self.grid[x][y] = self.label['path']  # Mark the path explicitly as 3, path
        else:
            print("No Path found")
            return None
        time.sleep(1)
        self.display_grid2()
        return path
        
def main():
    initial_grid = [
        [0, 0, 0, 7, 0, 0, 0],
        [0, 1, 0, 7, 0, 9, 0],
        [0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
    ]
    
    #HERE

    #grid.update_grid('obstacle', 7, 7)

if __name__ == "__main__":
    main()



