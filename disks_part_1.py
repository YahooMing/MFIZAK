import pygame
import random
import math

pygame.init()

width, height = 1960, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Kod Oskara Chrostowskiego")

N = 1000
disks = []
for _ in range(N):
    radius = random.randint(5, 10)
    mass = random.uniform(1, 5)
    x = random.uniform(radius, width - radius)
    y = random.uniform(radius, height - radius)
    vx = random.uniform(-2, 2)
    vy = random.uniform(-2, 2)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    disks.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'radius': radius, 'mass': mass, 'color': color})

cx, cy = width / 2, height / 2
G = 10
M = 200

def update_position(disk, dt):
    r = math.sqrt((disk['x'] - cx) ** 2 + (disk['y'] - cy) ** 2)
    if r != 0:
        fx = -G * M * (disk['x'] - cx) * disk['mass'] / (r**3 + 1000) #I had to add 1000 because otherwise some disks were shooting off in random directions
        fy = -G * M * (disk['y'] - cy) * disk['mass'] / (r**3 + 1000)
        ax = fx / disk['mass'] #geet
        ay = fy / disk['mass'] #geet
        disk['vx'] += ax * dt
        disk['vy'] += ay * dt
    disk['x'] += disk['vx'] * dt
    disk['y'] += disk['vy'] * dt

    if disk['x'] - disk['radius'] < 0 or disk['x'] + disk['radius'] > width:
        disk['vx'] *= -1
    if disk['y'] - disk['radius'] < 0 or disk['y'] + disk['radius'] > height:
        disk['vy'] *= -1


running = True
clock = pygame.time.Clock()
#frame_count = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    for disk in disks:
        update_position(disk, 0.5)
        pygame.draw.circle(screen, disk['color'], (int(disk['x']), int(disk['y'])), disk['radius'])

    pygame.display.flip()
    clock.tick(60)

    #pygame.image.save(screen, f"frame_{frame_count:04d}.png")
    #frame_count += 1

pygame.quit()