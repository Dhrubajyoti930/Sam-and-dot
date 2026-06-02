import math
import random
import time
import sys

# ENGINE MODULE A: THE LINEAR ALGEBRA & RENDERING MATHEMATICS
class Vector2D:
    __slots__ = ('x', 'y')
    def __init__(self, x: float, y: float):
        self.x, self.y = float(x), float(y)
    def __add__(self, o): return Vector2D(self.x + o.x, self.y + o.y)
    def __sub__(self, o): return Vector2D(self.x - o.x, self.y - o.y)
    def __mul__(self, s): return Vector2D(self.x * s, self.y * s)
    def dot(self, o): return self.x * o.x + self.y * o.y
    def length(self): return math.sqrt(self.x**2 + self.y**2)
    def normalize(self):
        l = self.length()
        return Vector2D(self.x/l, self.y/l) if l > 0 else Vector2D(0, 0)
    def rotate(self, deg):
        rad = math.radians(deg)
        s, c = math.sin(rad), math.cos(rad)
        return Vector2D(self.x * c - self.y * s, self.x * s + self.y * c)

class EngineMath:
    TRIG_CACHE = {i: (math.cos(math.radians(i)), math.sin(math.radians(i))) for i in range(360)}
    @staticmethod
    def get_cos(deg): return EngineMath.TRIG_CACHE[int(deg) % 360][0]
    @staticmethod
    def get_sin(deg): return EngineMath.TRIG_CACHE[int(deg) % 360][1]

# ENGINE MODULE C: THE GAME STATE, ENTITIES, & COLLISION
class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vector2D(x, y)
        self.dir = Vector2D(1, 0)
        self.plane = Vector2D(0, 0.66)
    def update(self, move_speed: float, rot_speed: float, world: list):
        next_pos = self.pos + (self.dir * move_speed)
        if world[int(self.pos.y)][int(next_pos.x)] == ' ':
            self.pos.x = next_pos.x
        if world[int(next_pos.y)][int(self.pos.x)] == ' ':
            self.pos.y = next_pos.y
        if rot_speed != 0:
            self.dir = self.dir.rotate(rot_speed)
            self.plane = self.plane.rotate(rot_speed)

# ENGINE MODULE D: THE PROCEDURAL CHRONICLE ENGINE
class NarrativeEngine:
    def __init__(self):
        self.version = "5.5.0"
        self.chronicle = [
            "The archive awakens. Memory sectors recalibrating...",
            "Lore synthesis active: Identifying forgotten static-fragments.",
            "Dimensional boundary integrity stable: Reality 5.5.0."
        ]
        self.lexicon = ["Omen", "Nexus", "Drift", "Static", "Echo", "Void-Gate"]
        self.tick = 0
    def fetch_narrative(self, pos: Vector2D) -> str:
        self.tick += 1
        node = self.lexicon[(int(pos.x) + int(pos.y)) % len(self.lexicon)]
        return f"DOT.py {self.version} | Sector: {node} | T:{self.tick:04d} | Log: {random.choice(self.chronicle)}"

# ENGINE MODULE B & E: RENDERING, RASTERIZATION & VIRTUAL FRAME BUFFER
class Engine:
    def __init__(self):
        self.width, self.height = 80, 24
        self.world = [
            "################################################################################",
            "#     #            #                                                           #",
            "#     #            #        #                                  #               #",
            "#                  #        #           #                      #               #",
            "#     ########     #        #           #      #######         #               #",
            "#                  #        #           #                      #               #",
            "#     #            #        #           #                      #               #",
            "#     #            #                                           #               #",
            "#                                                              #               #",
            "################################################################################"
        ]
        self.player = Player(4, 4)
        self.narrative = NarrativeEngine()
        self.vram = [[' ' for _ in range(self.width)] for _ in range(self.height)]

    def draw_pixel(self, x: int, y: int, char: str):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.vram[y][x] = char

    def render_frame(self):
        self.vram = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        for x in range(self.width):
            cam_x = 2 * x / self.width - 1
            ray_dir = self.player.dir + (self.player.plane * cam_x)
            map_pos = [int(self.player.pos.x), int(self.player.pos.y)]
            delta = Vector2D(abs(1/(ray_dir.x + 1e-9)), abs(1/(ray_dir.y + 1e-9)))
            step = [1 if ray_dir.x > 0 else -1, 1 if ray_dir.y > 0 else -1]
            side_dist = Vector2D(
                (self.player.pos.x - map_pos[0]) * delta.x if ray_dir.x < 0 else (map_pos[0] + 1 - self.player.pos.x) * delta.x,
                (self.player.pos.y - map_pos[1]) * delta.y if ray_dir.y < 0 else (map_pos[1] + 1 - self.player.pos.y) * delta.y
            )
            hit, side = False, 0
            while not hit:
                if side_dist.x < side_dist.y:
                    side_dist.x += delta.x
                    map_pos[0] += step[0]
                    side = 0
                else:
                    side_dist.y += delta.y
                    map_pos[1] += step[1]
                    side = 1
                if self.world[map_pos[1]][map_pos[0]] != ' ': hit = True
            
            perp_dist = (side_dist.x - delta.x) if side == 0 else (side_dist.y - delta.y)
            line_height = int(self.height / (perp_dist + 1e-3))
            draw_start = max(0, -line_height // 2 + self.height // 2)
            draw_end = min(self.height - 1, line_height // 2 + self.height // 2)
            shading = '@' if perp_dist < 2 else ('#' if perp_dist < 5 else (':' if perp_dist < 10 else '.'))
            for y in range(draw_start, draw_end): self.draw_pixel(x, y, shading)
        
        status = self.narrative.fetch_narrative(self.player.pos)
        for i, char in enumerate(status[:self.width]): self.draw_pixel(i, 0, char)

    def run(self):
        sys.stdout.write("\033[2J")
        try:
            while True:
                self.render_frame()
                rot = 2.0 if random.random() > 0.95 else 0
                self.player.update(0.15, rot, self.world)
                frame = "\033[H" + "\n".join(["".join(row) for row in self.vram])
                sys.stdout.write(frame)
                sys.stdout.flush()
                time.sleep(0.04)
        except KeyboardInterrupt:
            sys.stdout.write("\nNarrative Archive Saved. Engine Shutdown.\n")

if __name__ == "__main__":
    Engine().run()
