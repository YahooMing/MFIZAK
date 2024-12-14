from panda3d.core import Vec3, PointLight
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import TextNode
import random
import math
from panda3d.core import NodePath, Geom, GeomNode
from panda3d.core import GeomVertexFormat, GeomVertexData, GeomVertexWriter, GeomTriangles


class Particle:
    def __init__(self, position, velocity, color, lifespan, emitter_id):
        self.position = Vec3(position)
        self.velocity = Vec3(velocity)
        self.color = color
        self.lifespan = lifespan
        self.age = 0
        self.emitter_id = emitter_id


class Emitter:
    def __init__(self, position, rate, emitter_id, color, area_size=None):
        self.position = Vec3(position)
        self.rate = rate
        self.emitter_id = emitter_id
        self.color = color
        self.area_size = area_size

    def emit(self):
        if self.area_size:
            x = random.uniform(self.area_size[0], self.area_size[1])
            y = random.uniform(self.area_size[2], self.area_size[3])
            z = self.position.z
            position = Vec3(x, y, z)
        else:
            position = Vec3(self.position)

        velocity = Vec3(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-2, -1))
        #color = (random.random(), random.random(), random.random(), 1)
        lifespan = random.uniform(10, 12)
        return Particle(position, velocity, self.color, lifespan, self.emitter_id)


class ParticleSystem:
    def __init__(self, parent_node, emitters, max_particles=1500):
        self.particles = []
        self.emitters = emitters
        self.parent_node = parent_node
        self.max_particles = max_particles
        self.gravity = Vec3(0, 0, 9.8)
        self.external_force = Vec3(0, 0, 0)
        self.particle_nodes = []
        self.ground_areas = [(-10, 10, -10, 10)]

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

                if particle.position.z <= ground_level and self.is_over_ground(particle.position):
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

    def is_over_ground(self, position):
        for area in self.ground_areas:
            x_min, x_max, y_min, y_max = area
            if x_min <= position.x <= x_max and y_min <= position.y <= y_max:
                return True
        return False

class ParticleApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        self.setBackgroundColor(0.05, 0.05, 0.2, 1)

        self.camera_radius = 35
        self.camera_angle = 0
        self.camera_speed = 10


        emitter1 = Emitter(position=(0, 0, 10), rate=100, emitter_id=1, color=(255,255,255), area_size=(-9, 9, -9, 9))
        emitter2 = Emitter(position=(5, 0, 3), rate=100, emitter_id=0, color=(0,0,0))

        self.particle_system = ParticleSystem(self.render, [emitter1, emitter2])

        light = PointLight("point_light")
        light_node = self.render.attachNewNode(light)
        light_node.setPos(0, -10, 20)
        self.render.setLight(light_node)

        self.create_ground()
        self.tree = Tree(self.render)


        #self.sphere_radius = 1
        #self.sphere_position = Vec3(2, 2, 1)
        #self.sphere = self.loader.loadModel("models/misc/sphere")
        #self.sphere.setScale(self.sphere_radius)
        #self.sphere.setPos(self.sphere_position)
        #self.sphere.setColor(1, 0, 0, 1)
        #self.sphere.reparentTo(self.render)

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
        self.camera.setPos(x, y, 5)
        self.camera.lookAt(0, 0, 0)

        return Task.cont



    def update(self, task):
        dt = globalClock.getDt()

        if self.wind_active:
            #wind_force = (self.sphere_position - self.particle_system.emitters[0].position).normalized() * 20
            #self.particle_system.external_force = wind_force
            self.particle_system.external_force = Vec3(5, 0, 0)
        else:
            self.particle_system.external_force = Vec3(0, 0, 0)

        self.particle_system.update(dt, ground_level=0, collider_position=Vec3(0, 0, -10), collider_radius=0)

        num_particles = len(self.particle_system.particles)
        wind_status = "ON" if self.wind_active else "OFF"
        self.info_text.setText(
            f"Particles: {num_particles}\nPress 'W' to toggle wind\nWind: {wind_status}"
        )

        return Task.cont

class Tree:
    def __init__(self, parent_node):
        self.parent_node = parent_node
        self.tree_height = 1
        self.tree_radius = 5
        self.create_tree()

    def create_tree(self):
        trunk_height = 2
        trunk_radius = 0.5
        self.trunk = self.create_cylinder(position=(0, 0, 0), radius=trunk_radius, height=trunk_height, color=(0.6, 0.3, 0.1, 1))

        #self.create_branch_layer(self.tree_height-0.5, self.tree_radius-1.5)
        self.create_branch_layer(self.tree_height, self.tree_radius-2)
        self.create_branch_layer(self.tree_height + 1, self.tree_radius-2.5)
        self.create_branch_layer(self.tree_height + 2, self.tree_radius-3)
        self.create_branch_layer(self.tree_height + 3, self.tree_radius-3.5)
        self.create_branch_layer(self.tree_height + 4, self.tree_radius-4)
        self.create_branch_layer(self.tree_height + 5, self.tree_radius-4.5)

        self.create_sphere(position=(0, 0, self.tree_height + 7), radius=0.5, color=(0, 1, 0, 1))

    def create_branch_layer(self, height, radius):
        self.create_cylinder(position=(0, 0, height), radius=radius, height=2, color=(0, 1, 0, 1))

    def create_cylinder(self, position, radius, height, color):
        cylinder = self.create_geom_cylinder(radius, height)
        node = self.parent_node.attachNewNode(cylinder)
        node.setPos(position)
        node.setColor(*color)
        return node

    def create_geom_cylinder(self, radius, height):
        format = GeomVertexFormat.get_v3n3()
        vdata = GeomVertexData('cylinder', format, Geom.UHStatic)

        vertex_writer = GeomVertexWriter(vdata, 'vertex')
        normal_writer = GeomVertexWriter(vdata, 'normal')

        num_segments = 16
        angle_step = 2 * 3.14159 / num_segments

        for i in range(num_segments):
            angle = i * angle_step
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)

            vertex_writer.addData3f(x, y, 0)
            normal_writer.addData3f(0, 0, -1)

            vertex_writer.addData3f(x, y, height)
            normal_writer.addData3f(0, 0, 1)

        #This part doesn't work as it should, but have to leave it here
        tris = GeomTriangles(Geom.UHStatic)
        for i in range(num_segments):
            next_i = (i + 1) % num_segments

            tris.addVertex(i * 2)
            tris.addVertex(next_i * 2)
            tris.addVertex(i * 2 + 1)

            tris.addVertex(next_i * 2 + 1)
            tris.addVertex(i * 2 + 1)
            tris.addVertex(next_i * 2)

        geom = Geom(vdata)
        geom.addPrimitive(tris)
        geom_node = GeomNode('cylinder')
        geom_node.addGeom(geom)
        return geom_node

    def create_sphere(self, position, radius, color):
        sphere = loader.loadModel("models/misc/sphere")
        sphere.setScale(radius)
        sphere.setPos(position)
        sphere.setColor(*color)
        sphere.reparentTo(self.parent_node)


app = ParticleApp()
app.run()