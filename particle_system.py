from panda3d.core import Vec3, PointLight
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import TextNode
import random
import math


class Particle:
    def __init__(self, position, velocity, color, lifespan, emitter_id):
        self.position = Vec3(position)
        self.velocity = Vec3(velocity)
        self.color = color
        self.lifespan = lifespan
        self.age = 0
        self.emitter_id = emitter_id


class Emitter:
    def __init__(self, position, rate, emitter_id):
        self.position = Vec3(position)
        self.rate = rate
        self.emitter_id = emitter_id

    def emit(self):
        velocity = Vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(1, 3))
        color = (random.random(), random.random(), random.random(), 1)
        lifespan = random.uniform(2, 5)
        return Particle(self.position, velocity, color, lifespan, self.emitter_id)


class ParticleSystem:
    def __init__(self, parent_node, emitters, max_particles=1500):
        self.particles = []
        self.emitters = emitters
        self.parent_node = parent_node
        self.max_particles = max_particles
        self.gravity = Vec3(0, 0, 9.8)
        self.external_force = Vec3(0, 0, 0)
        self.particle_nodes = []

        self.particle_model = loader.loadModel("models/misc/sphere")
        self.particle_model.setScale(0.1)

    def update(self, dt, ground_level, collider_position, collider_radius):
        for emitter in self.emitters:
            for _ in range(int(emitter.rate * dt)):
                if len(self.particles) < self.max_particles:
                    particle = emitter.emit()
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
                if particle.emitter_id == 1:
                    particle.velocity += (Vec3(0, 0, -9.8) + self.external_force) * dt
                else:
                    particle.velocity += (self.gravity + self.external_force) * dt

                particle.position += particle.velocity * dt

                if particle.position.z <= ground_level:
                    particle.position.z = ground_level
                    particle.velocity = Vec3(0, 0, 0)

                to_collider = particle.position - collider_position
                if to_collider.length() <= collider_radius:
                    particle.velocity = Vec3(0, 0, 0)
                    particle.position = collider_position + to_collider.normalized() * collider_radius

                self.particle_nodes[i].setPos(particle.position)

    def create_particle_node(self, particle):
        node = self.particle_model.copyTo(self.parent_node)
        node.setPos(particle.position)
        node.setColor(*particle.color)
        return node


class ParticleApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        self.camera_radius = 25
        self.camera_angle = 0
        self.camera_speed = 10

        emitter1 = Emitter(position=(0, 0, 5), rate=200, emitter_id=1)
        emitter2 = Emitter(position=(5, 0, 3), rate=500, emitter_id=0)

        self.particle_system = ParticleSystem(self.render, [emitter1, emitter2])

        light = PointLight("point_light")
        light_node = self.render.attachNewNode(light)
        light_node.setPos(0, -10, 20)
        self.render.setLight(light_node)

        self.create_ground()

        self.sphere_radius = 1
        self.sphere_position = Vec3(2, 2, 1)
        self.sphere = self.loader.loadModel("models/misc/sphere")
        self.sphere.setScale(self.sphere_radius)
        self.sphere.setPos(self.sphere_position)
        self.sphere.setColor(1, 0, 0, 1)
        self.sphere.reparentTo(self.render)

        self.wind_active = False
        self.accept("w", self.toggle_wind)

        self.info_text = OnscreenText(
            text="",
            pos=(-1.2, 0.9),
            scale=0.05,
            align=TextNode.ALeft,
            fg=(1, 1, 1, 1),
            bg=(0, 0, 0, 0.5),
            mayChange=True,
        )

        self.taskMgr.add(self.update, "UpdateParticles")
        self.taskMgr.add(self.rotate_camera_around_center, "RotateCamera")

    def create_ground(self):
        from panda3d.core import CardMaker
        cm = CardMaker("ground")
        cm.setFrame(-10, 10, -10, 10)
        ground = self.render.attachNewNode(cm.generate())
        ground.setPos(0, 0, 0)
        ground.setHpr(0, -90, 0)
        ground.setColor(0.2, 0.8, 0.2, 1)

    def toggle_wind(self):
        self.wind_active = not self.wind_active

    def rotate_camera_around_center(self, task):
        dt = globalClock.getDt()
        self.camera_angle += self.camera_speed * dt
        angle_rad = math.radians(self.camera_angle)

        x = self.camera_radius * math.sin(angle_rad)
        y = self.camera_radius * math.cos(angle_rad)
        self.camera.setPos(x, y, 10)
        self.camera.lookAt(0, 0, 0)

        return Task.cont

    def update(self, task):
        dt = globalClock.getDt()

        if self.wind_active:
            wind_force = (self.sphere_position - self.particle_system.emitters[0].position).normalized() * 20
            self.particle_system.external_force = wind_force
        else:
            self.particle_system.external_force = Vec3(0, 0, 0)

        self.particle_system.update(dt, ground_level=0, collider_position=self.sphere_position, collider_radius=self.sphere_radius)

        num_particles = len(self.particle_system.particles)
        wind_status = "ON" if self.wind_active else "OFF"
        self.info_text.setText(
            f"Particles: {num_particles}\nPress 'W' to toggle wind\nWind: {wind_status}"
        )

        return Task.cont


app = ParticleApp()
app.run()
