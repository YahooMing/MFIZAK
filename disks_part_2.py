import pygame
import random
import math

pygame.init()

width, height = 1960, 1080
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Oskar Chrostowski's Simulation")

N = 100 #I had to decrease the number of disks because of collisions
G = 10
M = 200
radius_limit = 10
speed_limit = 2.0
paused = False
collisions_enabled = True
density_scale = 0.5

def generate_disks(N):
    disks = []
    for _ in range(N):
        radius = random.randint(5, radius_limit)
        mass = random.uniform(1, 5)
        x = random.uniform(radius, width - radius)
        y = random.uniform(radius, height - radius)
        vx = random.uniform(-speed_limit, speed_limit)
        vy = random.uniform(-speed_limit, speed_limit)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        disks.append({'x': x, 'y': y, 'vx': vx, 'vy': vy, 'radius': radius, 'mass': mass, 'color': color})
    return disks

disks = generate_disks(N)
cx, cy = width / 2, height / 2

def get_density(r):
    max_density = 0.01
    radius = 200
    if r < radius:
        return max_density
    else:
        return max_density * max(0, (1 - (r - radius) / radius) * density_scale)

def update_position(disk, dt):
    r = math.sqrt((disk['x'] - cx) ** 2 + (disk['y'] - cy) ** 2)
    density = get_density(r)
    if r != 0:
        fx = -G * M * (disk['x'] - cx) * disk['mass'] / (r**3 + 1000)
        fy = -G * M * (disk['y'] - cy) * disk['mass'] / (r**3 + 1000)
        resistance_fx = -6 * math.pi * disk['vx'] * density * disk['radius']
        resistance_fy = -6 * math.pi * disk['vy'] * density * disk['radius']
        #resistance_fx = 0
        #resistance_fy = 0
        ax = fx / disk['mass'] + resistance_fx
        ay = fy / disk['mass'] + resistance_fy
        disk['vx'] += ax * dt
        disk['vy'] += ay * dt

    disk['x'] += disk['vx'] * dt
    disk['y'] += disk['vy'] * dt

    if disk['x'] - disk['radius'] < 0 or disk['x'] + disk['radius'] > width:
        disk['vx'] *= -1
    if disk['y'] - disk['radius'] < 0 or disk['y'] + disk['radius'] > height:
        disk['vy'] *= -1

def check_collision(disk1, disk2):
    dx = disk2['x'] - disk1['x']
    dy = disk2['y'] - disk1['y']
    distance = math.sqrt(dx**2 + dy**2)
    return distance < disk1['radius'] + disk2['radius']

def resolve_collision(disk1, disk2):
    dx = disk2['x'] - disk1['x']
    dy = disk2['y'] - disk1['y']
    distance = math.sqrt(dx**2 + dy**2)

    if distance == 0:
        return

    nx = dx / distance
    ny = dy / distance

    tx = -ny
    ty = nx

    v1n = disk1['vx'] * nx + disk1['vy'] * ny
    v1t = disk1['vx'] * tx + disk1['vy'] * ty
    v2n = disk2['vx'] * nx + disk2['vy'] * ny
    v2t = disk2['vx'] * tx + disk2['vy'] * ty

    m1, m2 = disk1['mass'], disk2['mass']
    v1n_new = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
    v2n_new = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

    disk1['vx'] = v1n_new * nx + v1t * tx
    disk1['vy'] = v1n_new * ny + v1t * ty
    disk2['vx'] = v2n_new * nx + v2t * tx
    disk2['vy'] = v2n_new * ny + v2t * ty

    overlap = 0.5 * (disk1['radius'] + disk2['radius'] - distance)
    disk1['x'] -= overlap * nx
    disk1['y'] -= overlap * ny
    disk2['x'] += overlap * nx
    disk2['y'] += overlap * ny

def draw_info(surface, font, x, y):
    global N, G, M, paused, collisions_enabled, density_scale
    info_lines = [
        f"Number of Disks: {N}",
        f"Gravity (G): {G}",
        f"Central Mass (M): {M}",
        f"Simulation Status: {'Paused' if paused else 'Running'}",
        f"Collisions: {'Enabled' if collisions_enabled else 'Disabled'}",
        f"Density scale: {density_scale:.2f}",

        "",
        "Controls:",
        "P -> Pause/Resume",
        "Up/Down -> Change Gravity",
        "Left/Right -> Change Central Mass",
        "+/- -> Add/Remove Disks",
        "C -> Toggle Collisions",
        "R -> Reset Disks",
        "A/D -> Change density"
    ]
    padding = 10
    line_height = font.get_height() + 5
    background_width = 450
    background_height = len(info_lines) * line_height + padding * 2

    pygame.draw.rect(surface, (50, 50, 50), (x, y, background_width, background_height))
    pygame.draw.rect(surface, (200, 200, 200), (x, y, background_width, background_height), 2)

    for i, line in enumerate(info_lines):
        text_surface = font.render(line, True, (255, 255, 255))
        surface.blit(text_surface, (x + padding, y + padding + i * line_height))

running = True
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_UP:
                G += 1
            elif event.key == pygame.K_DOWN:
                G = max(1, G - 1)
            elif event.key == pygame.K_RIGHT:
                M += 10
            elif event.key == pygame.K_LEFT:
                M = max(10, M - 10)
            elif event.key == pygame.K_r:
                disks = generate_disks(N)
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                N += 100
                disks = generate_disks(N)
            elif event.key == pygame.K_MINUS:
                N = max(100, N - 100)
                disks = generate_disks(N)
            elif event.key == pygame.K_c:
                collisions_enabled = not collisions_enabled
            elif event.key == pygame.K_d:
                density_scale += 0.01
            elif event.key == pygame.K_a:
                density_scale -= 0.01
            elif event.key == pygame.K_ESCAPE:
                running = False
                break
            elif event.key == pygame.MOUSEBUTTONUP:
                position = pygame.mouse.get_pos()
                cx = position[0]
                cy = position[1]
                print("HEJAs")

    if not paused:
        screen.fill((0, 0, 0))
        for i, disk1 in enumerate(disks):
            update_position(disk1, 0.5)
            if collisions_enabled:  
                for j in range(i + 1, len(disks)):
                    disk2 = disks[j]
                    if check_collision(disk1, disk2):
                        resolve_collision(disk1, disk2)
            pygame.draw.circle(screen, disk1['color'], (int(disk1['x']), int(disk1['y'])), disk1['radius'])

    draw_info(screen, font, 10, 10)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
