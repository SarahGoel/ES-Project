import pygame
import sys
import time
import random
import datetime

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Traffic Light Control System")

# Colors
dark_bg = (30, 30, 30)
red = (255, 0, 0)
green = (0, 255, 0)
yellow = (255, 255, 0)
white = (255, 255, 255)
gray = (60, 60, 60)
blue = (0, 200, 255)

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20)

log_file = open("traffic_log.txt", "w")
log_file.write("Smart Traffic Light Log\n")
log_file.write("Started at: {}\n\n".format(datetime.datetime.now()))

class TrafficLight:
    def __init__(self, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation
        self.state = "red"

    def draw(self):
        casing_color = (50, 50, 50)
        if self.orientation == "vertical":
            pygame.draw.rect(screen, casing_color, (self.x, self.y, 20, 60))
            pygame.draw.circle(screen, red if self.state == "red" else (80, 0, 0), (self.x + 10, self.y + 10), 6)
            pygame.draw.circle(screen, yellow if self.state == "yellow" else (80, 80, 0), (self.x + 10, self.y + 30), 6)
            pygame.draw.circle(screen, green if self.state == "green" else (0, 80, 0), (self.x + 10, self.y + 50), 6)
        else:
            pygame.draw.rect(screen, casing_color, (self.x, self.y, 60, 20))
            pygame.draw.circle(screen, red if self.state == "red" else (80, 0, 0), (self.x + 10, self.y + 10), 6)
            pygame.draw.circle(screen, yellow if self.state == "yellow" else (80, 80, 0), (self.x + 30, self.y + 10), 6)
            pygame.draw.circle(screen, green if self.state == "green" else (0, 80, 0), (self.x + 50, self.y + 10), 6)

def draw_pedestrian_signal(active):
    text = "WALK" if active else "STOP"
    color = green if active else red
    pygame.draw.rect(screen, dark_bg, (650, 50, 120, 60))
    label = font.render(f"Pedestrian: {text}", True, color)
    screen.blit(label, (655, 60))
    x, y = 710, 90
    if active:
        pygame.draw.circle(screen, white, (x, y), 5)
        pygame.draw.line(screen, white, (x, y+5), (x, y+20), 2)
        pygame.draw.line(screen, white, (x, y+10), (x-5, y+15), 2)
        pygame.draw.line(screen, white, (x, y+10), (x+5, y+15), 2)
        pygame.draw.line(screen, white, (x, y+20), (x-5, y+30), 2)
        pygame.draw.line(screen, white, (x, y+20), (x+5, y+30), 2)

class Vehicle:
    def __init__(self, direction):
        self.direction = direction
        self.length = 40
        self.width = 20
        if direction == "N":
            self.x, self.y = 380, HEIGHT
            self.dx, self.dy = 0, -2
            self.color = blue
        elif direction == "S":
            self.x, self.y = 420, -self.length
            self.dx, self.dy = 0, 2
            self.color = (255, 165, 0)
        elif direction == "E":
            self.x, self.y = -self.length, 280
            self.dx, self.dy = 2, 0
            self.color = (128, 0, 128)
        elif direction == "W":
            self.x, self.y = WIDTH, 320
            self.dx, self.dy = -2, 0
            self.color = (0, 255, 255)

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        if self.direction in ["E", "W"]:
            body = pygame.Rect(self.x, self.y, self.length, self.width)
            wheel1 = pygame.Rect(self.x+5, self.y-3, 6, 6)
            wheel2 = pygame.Rect(self.x+28, self.y-3, 6, 6)
            wheel3 = pygame.Rect(self.x+5, self.y+self.width-3, 6, 6)
            wheel4 = pygame.Rect(self.x+28, self.y+self.width-3, 6, 6)
        else:
            body = pygame.Rect(self.x, self.y, self.width, self.length)
            wheel1 = pygame.Rect(self.x-3, self.y+5, 6, 6)
            wheel2 = pygame.Rect(self.x-3, self.y+28, 6, 6)
            wheel3 = pygame.Rect(self.x+self.width-3, self.y+5, 6, 6)
            wheel4 = pygame.Rect(self.x+self.width-3, self.y+28, 6, 6)

        pygame.draw.rect(screen, self.color, body)
        for wheel in [wheel1, wheel2, wheel3, wheel4]:
            pygame.draw.ellipse(screen, (0, 0, 0), wheel)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 40 if self.direction in ["E", "W"] else 20, 20 if self.direction in ["E", "W"] else 40)

class Pedestrian:
    def __init__(self, from_side="right"):
        self.from_side = from_side
        self.y = 290
        self.color = (255, 192, 203)
        self.crossing = False
        self.x = 700 if self.from_side == "right" else 100
        self.speed = -1.5 if self.from_side == "right" else 1.5

    def update(self, signal_active):
        if signal_active:
            self.crossing = True
        if self.crossing:
            self.x += self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)
        pygame.draw.line(screen, self.color, (self.x, self.y+5), (self.x, self.y+15), 2)
        pygame.draw.line(screen, self.color, (self.x, self.y+8), (self.x-4, self.y+12), 1)
        pygame.draw.line(screen, self.color, (self.x, self.y+8), (self.x+4, self.y+12), 1)
        pygame.draw.line(screen, self.color, (self.x, self.y+15), (self.x-3, self.y+20), 1)
        pygame.draw.line(screen, self.color, (self.x, self.y+15), (self.x+3, self.y+20), 1)

    def get_rect(self):
        return pygame.Rect(self.x - 5, self.y - 5, 10, 20)

def draw_road():
    screen.fill(dark_bg)
    pygame.draw.rect(screen, gray, (350, 0, 100, HEIGHT))
    pygame.draw.rect(screen, gray, (0, 250, WIDTH, 100))
    for i in range(350, 450, 20):
        pygame.draw.line(screen, white, (i, 240), (i + 10, 240), 2)
        pygame.draw.line(screen, white, (i, 360), (i + 10, 360), 2)
    for i in range(250, 350, 20):
        pygame.draw.line(screen, white, (340, i), (340, i + 10), 2)
        pygame.draw.line(screen, white, (460, i), (460, i + 10), 2)
    for i in range(270, 330, 10):
        pygame.draw.rect(screen, white, (380, i, 40, 5))
    for i in range(370, 430, 10):
        pygame.draw.rect(screen, white, (i, 280, 5, 40))

lights = {
    "N": TrafficLight(375, 200, "vertical"),
    "S": TrafficLight(405, 340, "vertical"),
    "E": TrafficLight(340, 275, "horizontal"),
    "W": TrafficLight(460, 305, "horizontal")
}

vehicles = []
pedestrians = []
last_spawn = time.time()
last_ped_spawn = time.time()

cycle_order = ["N", "E", "S", "W"]
current = 0
cycle_timer = 0
cycle_time = 5

running = True
pedestrian_active = False

while running:
    dt = clock.tick(60) / 1000
    cycle_timer += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    draw_road()

    for dir in lights:
        lights[dir].state = "red"
    active_dir = cycle_order[current]
    lights[active_dir].state = "green"

    for light in lights.values():
        light.draw()

    pedestrian_active = all(l.state == "red" for l in lights.values() if l != lights[active_dir])
    draw_pedestrian_signal(pedestrian_active)

    if time.time() - last_spawn > 1:
        vehicles.append(Vehicle(random.choice(["N", "S", "E", "W"])))
        last_spawn = time.time()

    if pedestrian_active and time.time() - last_ped_spawn > 2:
        side = random.choice(["left", "right"])
        pedestrians.append(Pedestrian(from_side=side))
        last_ped_spawn = time.time()

    for v in vehicles[:]:
        rect = v.get_rect()
        if ((v.direction == "N" and v.y <= 220 and lights["N"].state != "green") or
            (v.direction == "S" and v.y + 40 >= 340 and lights["S"].state != "green") or
            (v.direction == "E" and v.x + 40 >= 360 and lights["E"].state != "green") or
            (v.direction == "W" and v.x <= 460 and lights["W"].state != "green")):
            pass
        else:
            v.move()
        v.draw()
        if v.x < -60 or v.x > WIDTH + 60 or v.y < -60 or v.y > HEIGHT + 60:
            vehicles.remove(v)

    for p in pedestrians[:]:
        p.update(pedestrian_active)
        p.draw()
        if p.x < -20 or p.x > WIDTH + 20:
            pedestrians.remove(p)

        for v in vehicles:
            if p.get_rect().colliderect(v.get_rect()):
                pygame.draw.rect(screen, red, p.get_rect().inflate(10, 10), 2)
                log_file.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} - COLLISION DETECTED!\n")

    if int(cycle_timer) == 0:
        log_file.write("{} - Green Light: {}\n".format(datetime.datetime.now().strftime("%H:%M:%S"), active_dir))

    if cycle_timer >= cycle_time:
        current = (current + 1) % 4
        cycle_timer = 0

    pygame.display.update()

log_file.write("\nEnded at: {}\n".format(datetime.datetime.now()))
log_file.close()
pygame.quit()
