import time, math, os

# A simple 2D gravity simulator using ASCII rendering
WIDTH, HEIGHT = 60, 30

def main():
    px, py = 10.0, 15.0
    vx, vy = 0.0, 0.4
    cx, cy = 30.0, 15.0
    mass = 50.0
    
    for _ in range(200):
        # Gravity vector
        dx, dy = cx - px, cy - py
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 1.0: break
        
        force = mass / (dist**2)
        vx += (dx / dist) * force
        vy += (dy / dist) * force
        
        px += vx
        py += vy
        
        # Render
        grid = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
        grid[int(cy)][int(cx)] = 'O'
        if 0 <= int(py) < HEIGHT and 0 <= int(px) < WIDTH:
            grid[int(py)][int(px)] = '*'
        
        frame = "\n".join("".join(row) for row in grid)
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"Probe Pos: ({px:.1f}, {py:.1f}) | Velocity: ({vx:.2f}, {vy:.2f})")
        print(frame)
        time.sleep(0.05)

if __name__ == '__main__':
    main()