import time
import random
import os

class EntropyGarden:
    def __init__(self, width=40, height=20):
        self.w, self.h = width, height
        self.grid = [[random.choice([0, 1]) for _ in range(width)] for _ in range(height)]

    def count_neighbors(self, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0: continue
                nx, ny = (x + i) % self.w, (y + j) % self.h
                count += self.grid[ny][nx]
        return count

    def step(self):
        new_grid = [[0 for _ in range(self.w)] for _ in range(self.h)]
        for y in range(self.h):
            for x in range(self.w):
                neighbors = self.count_neighbors(x, y)
                if self.grid[y][x] == 1:
                    new_grid[y][x] = 1 if neighbors in [2, 3] else 0
                else:
                    new_grid[y][x] = 1 if neighbors == 3 else 0
        self.grid = new_grid

    def render(self):
        output = []
        for row in self.grid:
            output.append(''.join(['#' if cell else ' ' for cell in row]))
        print(os.linesep.join(output))

if __name__ == '__main__':
    garden = EntropyGarden()
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            garden.render()
            garden.step()
            time.sleep(0.15)
    except KeyboardInterrupt:
        print('\nGarden returned to silence.')