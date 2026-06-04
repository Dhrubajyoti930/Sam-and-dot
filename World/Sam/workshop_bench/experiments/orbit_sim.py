import time, math, os

# Configuration
WIDTH, HEIGHT = 60, 30
G = 1.0
MASS = 500.0

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

class Body:
    def __init__(self, x, y, vx, vy):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy

    def update(self):
        dx, dy = self.x - WIDTH/2, self.y - HEIGHT/2
        dist = math.sqrt(dx**2 + dy**2) or 1
        force = G * MASS / (dist**2)
        self.vx -= force * (dx / dist) * 0.5
        self.vy -= force * (dy / dist) * 0.5
        self.x += self.vx
        self.y += self.vy

def draw(body):
    grid = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
    grid[int(HEIGHT/2)][int(WIDTH/2)] = 'O'
    ix, iy = int(body.x), int(body.y)
    if 0 <= ix < WIDTH and 0 <= iy < HEIGHT:
        grid[iy][ix] = '*'
    return "\n".join("".join(row) for row in grid)

def main():
    # Launch satellite from the side
    ship = Body(WIDTH - 5, HEIGHT / 2, 0, -1.2)
    try:
        while True:
            clear()
            ship.update()
            print(f"Orbit Sim | Pos: ({ship.x:.1f}, {ship.y:.1f}) | Vel: ({ship.vx:.2f}, {ship.vy:.2f})")
            print(draw(ship))
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nSimulation ended.")

if __name__ == '__main__':
    main()