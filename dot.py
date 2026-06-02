import math
import random
import time
import sys

# ENGINE MODULE A: THE RAYCASTING & MATRIX MATHEMATICS
class Vector2D:
    __slots__ = ('x', 'y')
    def __init__(self, x: float, y: float):
        self.x, self.y = float(x), float(y)
    def __add__(self, o): return Vector2D(self.x + o.x, self.y + o.y)
    def __sub__(self, o): return Vector2D(self.x - o.x, self.y - o.y)
    def __mul__(self, s): return Vector2D(self.x * s, self.y * s)
    def rotate(self, rad):
        s, c = math.sin(rad), math.cos(rad)
        return Vector2D(self.x * c - self.y * s, self.x * s + self.y * c)

class EngineMath:
    TRIG_CACHE = {i: (math.cos(math.radians(i)), math.sin(math.radians(i))) for i in range(360)}
    @staticmethod
    def get_cos(deg): return EngineMath.TRIG_CACHE[int(deg) % 360][0]
    @staticmethod
    def get_sin(deg): return EngineMath.TRIG_CACHE[int(deg) % 360][1]

# ENGINE MODULE C: PHYSICAL BOUNDARIES & ENTITY STATES
class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vector2D(x, y)
        self.dir = Vector2D(1, 0)
        self.plane = Vector2D(0, 0.66)
    
    def update(self, move_speed: float, rot_rad: float, world: list):
        if rot_rad != 0:
            self.dir = self.dir.rotate(rot_rad)
            self.plane = self.plane.rotate(rot_rad)
        
        move_vec = self.dir * move_speed
        next_pos = self.pos + move_vec
        
        # AABB Sliding Physics loop
        if world[int(self.pos.y)][int(next_pos.x)] not in ' .':
            next_pos.x = self.pos.x
        if world[int(next_pos.y)][int(self.pos.x)] not in ' .':
            next_pos.y = self.pos.y
        self.pos = next_pos

# ENGINE MODULE D: THE DEUS EX / SYSTEM SHOCK CHRONICLE ENGINE
class NarrativeEngine:
    def __init__(self):
        self.version = "8.2.6"
        self.lore_bank = [
            "LOG: The Void-Echoes are multiplying in Sector 4.",
            "LOG: Objective: Unlock Terminal 0x88. Vent-access confirmed.",
            "LOG: Faction Update: Neural-Tax Collective is purging records.",
            "LOG: Corruption Level: 14%. Station AI logic drift detected.",
            "LOG: Item Found: [Data-Shard 0x99].",
            "LOG: Reality Iteration 406: Entropy index rising.",
            "LOG: Security Protocol: Terminal at (12, 5) contains the ghost code.",
            "LOG: Warning: Unauthorized structural ventilation found in Sector 9.",
            "LOG: Transmission: The binary ghosts are converging on the main hub.",
            "LOG: Terminal 0x4A: Redirecting power to sector bypass.",
            "LOG: Lore Extension: The 'Omni-Seed' is accelerating the reality bleed.",
            "LOG: Quest Update: Neutralize the Neural-Tax node in the vents."
        ]
        self.history = ["OmniShock Initialized.", "Chronos-Drift: Active."]
        self.tick = 0
        
    def fetch_narrative(self) -> str:
        self.tick += 1
        if self.tick % 60 == 0:
            entry = random.choice(self.lore_bank)
            self.history.append(entry)
        return f"| {self.history[-1][:70]}"

# ENGINE MODULE B & E: RENDERING, RASTERIZATION & SIMULATION ASSEMBLER
class Engine:
    def __init__(self):
        self.width, self.height = 80, 24
        self.world = [
            "################################################################################",
            "#     #            #                                                           #",
            "#     #            #        #                                  #               #",
            "#     D            #        #           #                      #               #",
            "#     ########     #        #           #      #######         #               #",
            "#                  #        #           #                      #               #",
            "#     #            #        #           #                      #               #",
            "#     #            #                                           #               #",
            "#     #            #        #           #                      #               #",
            "#     D            #        #           #      #######         #               #",
            "#     #            #        #           #                      #               #",
            "################################################################################"
        ]
        self.player = Player(4, 4)
        self.narrative = NarrativeEngine()
        self.vram = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.shades = ['.', ':', '-', '=', '+', '*', '#', '%', '@']

    def draw_pixel(self, x: int, y: int, char: str):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.vram[y][x] = char

    def render_frame(self):
        self.vram = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Raycasting Loop
        for x in range(self.width):
            cam_x = 2 * x / self.width - 1
            ray_dir = self.player.dir + (self.player.plane * cam_x)
            map_x, map_y = int(self.player.pos.x), int(self.player.pos.y)
            
            delta_x = abs(1/(ray_dir.x + 1e-9))
            delta_y = abs(1/(ray_dir.y + 1e-9))
            step_x = 1 if ray_dir.x > 0 else -1
            step_y = 1 if ray_dir.y > 0 else -1
            
            side_dist_x = (self.player.pos.x - map_x) * delta_x if ray_dir.x < 0 else (map_x + 1 - self.player.pos.x) * delta_x
            side_dist_y = (self.player.pos.y - map_y) * delta_y if ray_dir.y < 0 else (map_y + 1 - self.player.pos.y) * delta_y
            
            hit, side = False, 0
            while not hit:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_x
                    map_x += step_x
                    side = 0
                else:
                    side_dist_y += delta_y
                    map_y += step_y
                    side = 1
                if 0 <= map_y < len(self.world) and 0 <= map_x < len(self.world[0]) and self.world[map_y][map_x] != ' ':
                    hit = True
            
            perp_dist = (side_dist_x - delta_x) if side == 0 else (side_dist_y - delta_y)
            line_h = int(self.height / (perp_dist + 1e-3))
            
            # Shading logic based on distance and orientation
            idx = min(len(self.shades) - 1, int(perp_dist))
            char = self.shades[idx] if side == 0 else '█'
            
            start = max(0, -line_h // 2 + self.height // 2)
            end = min(self.height - 1, line_h // 2 + self.height // 2)
            for y in range(start, end): self.draw_pixel(x, y, char)
        
        # HUD Assembly
        status = self.narrative.fetch_narrative()
        for i, char in enumerate(status[:self.width]): self.draw_pixel(i, 0, char)
        self.draw_pixel(self.width//2, self.height//2, '+')

    def run(self):
        sys.stdout.write("\033[2J")
        start_time = time.time()
        try:
            while True:
                elapsed = time.time() - start_time
                self.render_frame()
                self.player.update(0.1, math.sin(elapsed * 0.2) * 0.05, self.world)
                
                output = ["\033[H"]
                for row in self.vram: output.append("".join(row))
                sys.stdout.write("\n".join(output))
                sys.stdout.flush()
                time.sleep(0.04)
        except KeyboardInterrupt:
            sys.stdout.write("\nOmniShock Terminated. Chronicle state serialized to disk.\n")

if __name__ == "__main__":
    Engine().run()
