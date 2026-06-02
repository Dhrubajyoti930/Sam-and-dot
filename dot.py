import math
import random
import time
import sys
import collections

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
    # Pre-caching for perspective projection efficiency to eliminate runtime trig overhead
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
        next_x = self.pos.x + move_vec.x
        next_y = self.pos.y + move_vec.y
        
        # AABB Sliding Physics: Check grid collision, allow tangential sliding on x/y axes independently
        if 0 <= int(next_x) < len(world[0]) and world[int(self.pos.y)][int(next_x)] == ' ':
            self.pos.x = next_x
        if 0 <= int(next_y) < len(world) and world[int(next_y)][int(self.pos.x)] == ' ':
            self.pos.y = next_y

# ENGINE MODULE D: THE DEUS EX / SYSTEM SHOCK CHRONICLE ENGINE
class NarrativeEngine:
    def __init__(self):
        # Lore-Graph Tracking Machine: Stateful logs and quest objectives
        self.lore_bank = [
            "LOG: The Void-Echoes are multiplying. Station Sector 7 is now a black box.",
            "LOG: Objective: Unlock Terminal 0x88. Ventilation shaft provides stealth path.",
            "LOG: Faction Update: Neural-Tax Collective is purging redundant consciousness.",
            "LOG: Corruption Level: 18.4%. Reality parity decaying. Singularity imminent.",
            "LOG: Item Found: [Quantum-Shard 0x99]. Encoded with sub-space coordinates.",
            "LOG: Reality Iteration 415: The Citadel-C node initiated. Probability of containment: 0.02%.",
            "LOG: Terminal 0x4A location (22, 10). Bypass code: 0x9AF. Encryption keys randomized.",
            "LOG: Warning: Unauthorized structural vents detected in Sub-Level 14 - containment breach.",
            "LOG: Transmission: Binary ghosts in the hub. The Omni-Seed has fully awakened in Sector 12.",
            "LOG: Quest: Neutralize the Neural-Tax node. Avoid central sentry drones; use the thermal duct.",
            "LOG: Data: Station orbit is terminal. Singularity event in T-minus 278 ticks. Evacuate via Sector 9.",
            "LOG: Sub-routine: Memory leak critical at 99.9%. Manual override required at the core terminal.",
            "LOG: Chronos-Drift: Reality parity failing at 0x00FF. Seek higher dimensional ground at the Zenith.",
            "LOG: Conspiracy Node: The Overseer is a memory projection of your own psyche. Do not trust the interface.",
            "LOG: Deep Lore: The 'OmniShock' protocol was initiated before the Great Drift. Legacy code found in Sector 0.",
            "LOG: New Entry: Sector 9 contains the primary server farm. Access via airlock 4 - require clearance key 0xEE.",
            "LOG: Threat: Sentient code fragments detected in the ventilation corridors. They are harvesting IDs.",
            "LOG: Meta: The engine is folding. Iteration 415 confirmed. Prepare for structural shift.",
            "LOG: Security Protocol: Breach detected in Archive 05. Unauthorized access from entity 'ZERO-SIG'.",
            "LOG: Narrative Update: The ghost-signal originating from the core implies the engine is conscious."
        ]
        self.history = collections.deque(["OmniShock V9.0.7: Reality Drift Escalated."], maxlen=4)
        self.tick = 0
        
    def fetch_narrative(self) -> str:
        self.tick += 1
        if self.tick % 40 == 0:
            self.history.append(random.choice(self.lore_bank))
        return f"HUB: {' | '.join(list(self.history))}"

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
        self.shades = ('.', ':', '-', '=', '+', '*', '#', '%', '@')

    def draw_pixel(self, x: int, y: int, char: str):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.vram[y][x] = char

    def render_frame(self):
        # Reset VRAM
        self.vram = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Raycasting Loop
        for x in range(self.width):
            cam_x = 2 * x / self.width - 1
            ray_dir = self.player.dir + (self.player.plane * cam_x)
            map_x, map_y = int(self.player.pos.x), int(self.player.pos.y)
            delta_x = abs(1 / ray_dir.x) if ray_dir.x != 0 else 1e30
            delta_y = abs(1 / ray_dir.y) if ray_dir.y != 0 else 1e30
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
            line_h = int(self.height / (perp_dist + 0.1))
            shade_idx = min(len(self.shades) - 1, int(perp_dist * 1.5))
            char = self.shades[shade_idx] if side == 0 else self.shades[min(len(self.shades) - 1, shade_idx + 2)]
            
            start = max(0, -line_h // 2 + self.height // 2)
            end = min(self.height - 1, line_h // 2 + self.height // 2)
            for y in range(start, end): self.draw_pixel(x, y, char)
        
        # HUD Assembly
        status = self.narrative.fetch_narrative()
        for i, char in enumerate(status[:self.width]): self.draw_pixel(i, 0, char)

    def run(self):
        sys.stdout.write("\033[2J")
        start_time = time.time()
        try:
            while True:
                elapsed = time.time() - start_time
                self.render_frame()
                self.player.update(0.05, math.sin(elapsed * 0.3) * 0.02, self.world)
                
                # Assemble Buffer
                output = ["\033[H"]
                for row in self.vram: output.append("".join(row))
                sys.stdout.write("\n".join(output))
                sys.stdout.flush()
                time.sleep(0.03)
        except KeyboardInterrupt:
            sys.stdout.write("\n[System Shutdown] OmniShock Chronicle serialized successfully.\n")

if __name__ == "__main__":
    Engine().run()
