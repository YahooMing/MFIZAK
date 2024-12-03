from panda3d.core import Vec3, PointLight, CardMaker
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import random
import math


class Particle:
    def __init__(self, position, velocity, color, lifespan):
        self.position = Vec3(position)
        self.velocity = Vec3(velocity)
        self.color = color
        self.lifespan = lifespan
        self.age = 0


class Emitter:
    def __init__(self, position, rate):
        self.position = Vec3(position)
        self.rate = rate

    def emit(self):
        velocity = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(1, 3))
        color = (random.random(), random.random(), random.random(), 1)
        lifespan = random.uniform(2, 5)
        return Particle(self.position, velocity, color, lifespan)


class ParticleSystem:
    def __init__(self, parent_node, emitter, max_particles=1000):
        self.particles = []
        self.emitter = emitter
        self.parent_node = parent_node
        self.max_particles = max_particles
        self.gravity = Vec3(0, 0, -9.8)
        self.external_force = Vec3(0, 0, 0)
        self.particle_nodes = []

        # Załaduj model sfery dla cząsteczek
        self.particle_model = loader.loadModel("models/misc/sphere")  # Użycie modelu sfery
        self.particle_model.setScale(0.1)  # Rozmiar cząsteczek

    def update(self, dt, ground_level):
        for _ in range(int(self.emitter.rate * dt)):
            if len(self.particles) < self.max_particles:
                particle = self.emitter.emit()
                node = self.create_particle_node(particle)
                self.particles.append(particle)
                self.particle_nodes.append(node)

        for i in reversed(range(len(self.particles))):
            particle = self.particles[i]
            particle.age += dt

            if particle.age > particle.lifespan:
                self.particles.pop(i)
                self.particle_nodes[i].removeNode()
                self.particle_nodes.pop(i)
            else:
                particle.velocity += (self.gravity + self.external_force) * dt
                particle.position += particle.velocity * dt

                # Kolizja z podłogą
                if particle.position.z <= ground_level:
                    particle.position.z = ground_level
                    particle.velocity = Vec3(0, 0, 0)

                self.particle_nodes[i].setPos(particle.position)

    def create_particle_node(self, particle):
        node = self.particle_model.copyTo(self.parent_node)
        node.setPos(particle.position)
        node.setColor(*particle.color)  # Przypisanie koloru cząsteczki
        return node


class ParticleApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        self.camera_radius = 25
        self.camera_angle = 0
        self.camera_speed = 10  # Stopnie na sekundę

        emitter = Emitter(position=(0, 0, 5), rate=500)
        self.particle_system = ParticleSystem(self.render, emitter)

        light = PointLight("point_light")
        light_node = self.render.attachNewNode(light)
        light_node.setPos(0, -10, 20)
        self.render.setLight(light_node)

        self.create_ground()
        self.taskMgr.add(self.update, "UpdateParticles")
        self.taskMgr.add(self.rotate_camera_around_center, "RotateCamera")

    def create_ground(self):
        # Zamiast używać `grid.egg`, stwórzmy prostą podłogę za pomocą CardMaker
        from panda3d.core import CardMaker
        cm = CardMaker("ground")
        cm.setFrame(-10, 10, -10, 10)  # Prostokąt 20x20 jednostek
        ground = self.render.attachNewNode(cm.generate())
        ground.setPos(0, 0, 0)  # Pozycja podłogi
        ground.setHpr(0, -90, 0)  # Ustawienie podłogi poziomo
        ground.setColor(0.2, 0.8, 0.2, 1)  # Kolor zielony

    def rotate_camera_around_center(self, task):
        dt = globalClock.getDt()
        self.camera_angle += self.camera_speed * dt
        angle_rad = math.radians(self.camera_angle)

        # Oblicz nową pozycję kamery
        x = self.camera_radius * math.sin(angle_rad)
        y = self.camera_radius * math.cos(angle_rad)
        self.camera.setPos(x, y, 10)
        self.camera.lookAt(0, 0, 0)

        return Task.cont

    def update(self, task):
        dt = globalClock.getDt()
        self.particle_system.update(dt, ground_level=0)
        return Task.cont


app = ParticleApp()
app.run()
