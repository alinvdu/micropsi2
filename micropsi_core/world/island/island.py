import math
import os
import logging
from micropsi_core.world.world import World
from micropsi_core.world.worldadapter import WorldAdapter
from micropsi_core.world.worldobject import WorldObject
from micropsi_core.world.island import png


class Island(World):
    """ A simple Doerner Island-World"""

    supported_worldadapters = ['Braitenberg', 'Survivor', 'StructuredObjects', 'ElectricRobot']

    groundmap = {
        'image': "psi_1.png",
        'start_position': (700, 400),
        'scaling': (8, 8)
    }

    assets = {
        'background': "island/psi_1.png",
        'template': 'island/island.tpl',
        'paperjs': "island/island.js",
        'x': 2048,
        'y': 2048,
        'icons': {
            'Lightsource': 'island/lamp.png',
            'Braitenberg': 'island/braitenberg.png',
            'ElectricRobot': 'island/robot-small.png',
            'Survivor': 'island/Micropsi.png',
            'PalmTree': 'island/palm-tree.png',
            'Maple': 'island/maple.png',
            'Braintree': 'island/braintree.png',
            'Wirselkraut': 'island/wirselkraut.png',
            'Thornbush': 'island/unknownbox.png',
            'Juniper': 'island/juniper-berries.png',
            'Champignon': 'island/boletus-edulis.png',
            'FlyAgaric': 'island/fly-agaris.png',
            'Stone': 'island/rock.png',
            'Boulder': 'island/boulder.png',
            'Menhir': 'island/menhir.png',
            'Waterhole': 'island/well.png'
        }
    }

    def __init__(self, filename, world_type="Island", name="", owner="", engine=None, uid=None, version=1, config={}):
        World.__init__(self, filename, world_type=world_type, name=name, owner=owner, uid=uid, version=version)
        self.load_groundmap()
        # self.current_step = 0
        self.data['assets'] = self.assets

    def load_groundmap(self):
        """
        Imports a groundmap for an island world from a png file. We expect a bitdepth of 8 (i.e. each pixel defines
        a point with one of 256 possible values).
        """
        filename = os.path.join(os.path.dirname(__file__), 'resources', 'groundmaps', self.groundmap["image"])
        with open(filename, 'rb') as file:
            png_reader = png.Reader(file)
            x, y, image_array, image_params = png_reader.read()
            self.ground_data = list(image_array)
            self.scale_x = self.groundmap["scaling"][0]
            self.scale_y = self.groundmap["scaling"][1]
            self.x_max = x - 1
            self.y_max = y - 1

    def get_ground_at(self, x, y):
        """
        returns the ground type (an integer) at the given position
        """
        _x = int(min(self.x_max, max(0, round(x / self.scale_x))))
        _y = int(min(self.y_max, max(0, round(y / self.scale_y))))
        return self.ground_data[_y][_x]

    def get_brightness_at(self, position):
        """calculate the brightness of the world at the given position; used by sensors of agents"""
        brightness = 0
        for key in self.objects:
            if hasattr(self.objects[key], "get_intensity"):
                # adapted from micropsi1
                pos = self.objects[key].position
                diff = (pos[0] - position[0], pos[1] - position[1])
                dist = _2d_vector_norm(diff) + 1
                lightness = self.objects[key].get_intensity()
                brightness += (lightness /dist /dist)
        return brightness

    def get_movement_result(self, start_position, effort_vector, diameter=0):
        """determine how much an agent moves in the direction of the effort vector, starting in the start position.
        Note that agents may be hindered by impassable terrain and other objects"""

        efficiency = ground_types[self.get_ground_at(*start_position)]['move_efficiency']
        if not efficiency:
            return start_position
        movement_vector = (effort_vector[0] * efficiency, effort_vector[1] * efficiency)

        # make sure we don't bump into stuff
        target_position = None
        while target_position is None and _2d_distance_squared((0, 0), movement_vector) > 0.01:
            target_position = _2d_translate(start_position, movement_vector)

            for i in self.objects.values():
                if _2d_distance_squared(target_position, i.position) < (diameter + i.diameter) / 2:
                    movement_vector = (movement_vector[0] * 0.5, movement_vector[1] * 0.5)  # should be collision point
                    target_position = None
                    break

        if target_position is not None and ground_types[self.get_ground_at(target_position[0], target_position[1])]['agent_allowed']:
            return target_position
        else:
            return start_position


class Lightsource(WorldObject):
    """A pretty inert and boring light source, with a square falloff"""

    @property
    def diameter(self):
        return self.data.get('diameter', 1.)

    @diameter.setter
    def diameter(self, diameter):
        self.data['diameter'] = diameter

    @property
    def intensity(self):
        return self.data.get('intensity', 10000.)

    @intensity.setter
    def intensity(self, intensity):
        self.data['intensity'] = intensity

    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)

    def get_intensity(self, falloff_func=1.):
        """returns the strength of the light, optionally depending on a given fall-off function"""
        return self.intensity * self.diameter * self.diameter / falloff_func

    def action_eat(self):
        return True, 0, 0, -0.7

    def action_drink(self):
        return False, 0, 0, 0


class PalmTree(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "PalmTree"

    def action_eat(self):
        return False, 0, 0, 0

    def action_drink(self):
        return False, 0, 0, 0


class Maple(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Maple"

    def action_eat(self):
        return False, 0, 0, 0

    def action_drink(self):
        return False, 0, 0, 0


class Braintree(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Braintree"

    def action_eat(self):
        return False, 0, 0, 0

    def action_drink(self):
        return False, 0, 0, 0


class Wirselkraut(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Wirselkraut"

    def action_eat(self):
        return True, 0, 0, 0.5

    def action_drink(self):
        return False, 0, 0, 0


class Thornbush(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Thornbush"

    def action_eat(self):
        logging.getLogger("world").debug("... and the whirlwind is in the thorn tree...")
        return True, 0, 0, -0.1

    def action_drink(self):
        return False, 0, 0, 0


class Juniper(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Juniper"

    def action_eat(self):
        return True, 0.1, 0.1, 0

    def action_drink(self):
        return False, 0, 0, 0


class Champignon(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Champignon"

    def action_eat(self):
        return True, 0.3, 0, 0

    def action_drink(self):
        return True, 0, 0, 0


class FlyAgaric(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "FlyAgaric"

    def action_eat(self):
        return True, 0.1, 0, -0.9

    def action_drink(self):
        return False, 0, 0, 0


class Stone(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Stone"

    def action_eat(self):
        return False, 0, 0, 0

    def action_drink(self):
        return False, 0, 0, 0


class Boulder(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Boulder"

    def action_eat(self):
        return False, 0, 0, 0

    def action_drink(self):
        return False, 0, 0, 0


class Menhir(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Menhir"

    def action_eat(self):
        return False, 0, 0, 0

    def action_drink(self):
        return False, 0, 0, 0


class Waterhole(WorldObject):
    def __init__(self, world, uid=None, **data):
        WorldObject.__init__(self, world, category="objects", uid=uid, **data)
        self.structured_object_type = "Waterhole"

    def action_eat(self):
        return False, 0, 0, 0

    def action_drink(self):
        return True, 0, 1, 0


class Survivor(WorldAdapter):


    def __init__(self, world, uid=None, **data):
        super(Survivor, self).__init__(world, uid, **data)

        self.datasources = dict((s, 0) for s in ['body-energy', 'body-water', 'body-integrity'])
        self.datatargets = dict((t, 0) for t in ['action_eat', 'action_drink', 'loco_north', 'loco_south', 'loco_east', 'loco_west'])

        self.currentobject = None

        self.energy = 1.0
        self.water = 1.0
        self.integrity = 1.0
        self.is_dead = False

        self.action_cooloff = 5

        self.datasources['body-energy'] = self.energy
        self.datasources['body-water'] = self.water
        self.datasources['body-integrity'] = self.integrity

    def initialize_worldobject(self, data):
        if "position" not in data:
            self.position = self.world.groundmap['start_position']

    def update_data_sources_and_targets(self):
        """called on every world calculation step to advance the life of the agent"""

        if self.is_dead:
            return

        effortvector = ((50*self.datatargets['loco_east'])+(50 * -self.datatargets['loco_west']),
                        (50*self.datatargets['loco_north'])-(50* -self.datatargets['loco_south']))
        desired_position = (self.position[0] + effortvector[0], self.position[1] + effortvector[1])
        self.datatargets['loco_east'] = 0
        self.datatargets['loco_west'] = 0
        self.datatargets['loco_north'] = 0
        self.datatargets['loco_south'] = 0

        if ground_types[self.world.get_ground_at(desired_position[0], desired_position[1])]['agent_allowed']:
            self.position = desired_position

        #find nearest object to load into the scene
        lowest_distance_to_worldobject = float("inf")
        nearest_worldobject = None
        for key, worldobject in self.world.objects.items():
            # TODO: use a proper 2D geometry library
            distance = _2d_distance_squared(self.position, worldobject.position)
            if distance < lowest_distance_to_worldobject:
                lowest_distance_to_worldobject = distance
                nearest_worldobject = worldobject

        if self.currentobject is not nearest_worldobject and hasattr(nearest_worldobject, "structured_object_type"):
            self.currentobject = nearest_worldobject
            logging.getLogger("agent.%s" % self.uid).debug("Survivor WA selected new scene: %s",
                                             self.currentobject.structured_object_type)
        self.manage_body_parameters(nearest_worldobject)

    def manage_body_parameters(self, nearest_worldobject):
        """called by update() to update energy, water and integrity"""

        for datatarget in self.datatargets:
            if datatarget.startswith("action_"):
                self.datatarget_feedback[datatarget] = 0
                if self.datatargets[datatarget] >= 1 and self.action_cooloff <= 0:
                    self.datatargets[datatarget] = 0
                    if hasattr(nearest_worldobject, datatarget):
                        cando, delta_energy, delta_water, delta_integrity = nearest_worldobject.action_eat()
                    else:
                        cando, delta_energy, delta_water, delta_integrity = False, 0, 0, 0
                    if cando:
                        self.action_cooloff = 6
                        self.energy += delta_energy
                        self.water += delta_water
                        self.integrity += delta_integrity
                        self.datatarget_feedback[datatarget] = 1
                        logging.getLogger("agent.%s" % self.uid).debug("Agent "+self.name+" "+ datatarget +
                                                         "("+nearest_worldobject.data["type"]+") result: "+
                                                         " energy "+str(delta_energy)+
                                                         " water "+str(delta_water)+
                                                         " integrity "+str(delta_integrity))
                    else:
                        logging.getLogger("agent.%s" % self.uid).debug("Agent "+self.name+" "+ datatarget +
                                                         "("+nearest_worldobject.data["type"]+") result: "+
                                                         "cannot do.")

        self.action_cooloff -= 1
        self.energy -= 0.005
        self.water -= 0.005

        if self.energy > 1: self.energy = 1
        if self.water > 1: self.water = 1
        if self.integrity > 1: self.integrity = 1

        if self.energy <= 0 or self.water <= 0 or self.integrity <= 0:
            self.is_dead = True
            logging.getLogger("agent.%s" % self.uid).debug("Agent "+self.name+" has died:"+
                    " energy "+str(self.energy)+
                    " water "+str(self.water)+
                    " integrity "+str(self.integrity))

        self.datasources["body-energy"] = self.energy
        self.datasources["body-water"] = self.water
        self.datasources["body-integrity"] = self.integrity

    def is_alive(self):
        """called by the world to check whether the agent has died and should be removed"""
        return not self.is_dead


class Braitenberg(WorldAdapter):
    """A simple Braitenberg vehicle chassis, with two light sensitive sensors and two engines"""

    # positions of sensors, relative to origin of agent center
    brightness_l_offset = (-25, -50)
    brightness_r_offset = (+25, -50)

    # positions of engines, relative to origin of agent center
    engine_l_offset = (-25, 0)
    engine_r_offset = (+25, 0)

    # agent diameter
    diameter = 50  # note: this is also used as the distance between the wheels
    radius = 25

    # maximum speed
    speed_limit = 1.

    def __init__(self, world, uid=None, **data):
        super(Braitenberg, self).__init__(world, uid, **data)

        self.datasources = {'brightness_l': 0, 'brightness_r': 0}
        self.datatargets = {'engine_l': 0, 'engine_r': 0}
        self.datatarget_feedback = {'engine_l': 0, 'engine_r': 0}

    def initialize_worldobject(self, data):
        if "position" not in data:
            self.position = self.world.groundmap['start_position']

    def update_data_sources_and_targets(self):
        """called on every world calculation step to advance the life of the agent"""

        # drive engines
        l_wheel_speed = self.datatargets["engine_l"]
        r_wheel_speed = self.datatargets["engine_r"]

        # constrain speed
        if l_wheel_speed + r_wheel_speed > 2 * self.speed_limit:  # too fast
            f = 2 * self.speed_limit / (l_wheel_speed + r_wheel_speed)
            r_wheel_speed *= f
            l_wheel_speed *= f

        # (left - right) because inverted rotation circle ( doesn't change x because cosine, does change y because sine :)
        rotation = math.degrees((self.radius * l_wheel_speed - self.radius * r_wheel_speed) / self.diameter)
        self.orientation += rotation
        avg_velocity = (self.radius * r_wheel_speed + self.radius * l_wheel_speed) / 2
        translation = _2d_rotate((0, avg_velocity), self.orientation + rotation)

        # you may decide how far you want to go, but it is up the world to decide how far you make it
        self.position = self.world.get_movement_result(self.position, translation, self.diameter)

        # sense light sources
        brightness_l_position = _2d_translate(_2d_rotate(self.brightness_l_offset, self.orientation), self.position)
        brightness_r_position = _2d_translate(_2d_rotate(self.brightness_r_offset, self.orientation), self.position)

        brightness_l = self.world.get_brightness_at(brightness_l_position)
        brightness_r = self.world.get_brightness_at(brightness_r_position)

        self.datasources['brightness_l'] = brightness_l
        self.datasources['brightness_r'] = brightness_r
        
class ElectricRobot(WorldAdapter):
    """A robot-like agent with energy that can move using leg engines and charge from energy sources.
       If energy reaches zero, the robot does not die, but becomes effectively 'discharged' (cannot move)."""

    # Movement geometry parameters similar to a bipedal or wheeled system, adjusting if needed
    diameter = 50
    radius = 25
    speed_limit = 1.0

    def __init__(self, world, uid=None, **data):
        super(ElectricRobot, self).__init__(world, uid, **data)

        # The robot starts with full energy
        self.energy = 1.0

        # It never dies, but can become discharged (energy=0)
        self.is_discharged = False

        # Data sources: one for energy
        self.datasources = {
            'energy': self.energy
        }

        # Data targets for movement and charging
        self.datatargets = {
            'leg_engine_l': 0,
            'leg_engine_r': 0,
            'action_charge': 0
        }

        # Feedback
        self.datatarget_feedback = {
            'leg_engine_l': 0,
            'leg_engine_r': 0,
            'action_charge': 0
        }

        # Orientation and position
        self.orientation = 0.0
        if "position" in data:
            self.position = data["position"]
        else:
            self.position = self.world.groundmap.get('start_position', (0, 0))

    def initialize_worldobject(self, data):
        if "position" not in data:
            self.position = self.world.groundmap.get('start_position', (0, 0))

    def update_data_sources_and_targets(self):
        # If energy is zero, consider it discharged; it cannot move or do actions that cost energy
        if self.energy <= 0:
            self.energy = 0
            self.is_discharged = True
        else:
            self.is_discharged = False

        # Movement only if not discharged
        if not self.is_discharged:
            self.apply_movement()

        nearest_worldobject = self.find_nearest_worldobject()

        # Handle charge action if requested
        self.handle_actions(nearest_worldobject)

        # Update energy costs (even if not moving, there's a small upkeep)
        self.update_energy_costs()

        # Update datasource
        self.datasources["energy"] = self.energy

    def apply_movement(self):
        l_speed = self.datatargets["leg_engine_l"]
        r_speed = self.datatargets["leg_engine_r"]

        # Reset datatargets after reading
        self.datatargets["leg_engine_l"] = 0
        self.datatargets["leg_engine_r"] = 0

        # Constrain speed if too high
        if l_speed + r_speed > 2 * self.speed_limit:
            f = 2 * self.speed_limit / (l_speed + r_speed)
            r_speed *= f
            l_speed *= f

        rotation = math.degrees((self.radius * l_speed - self.radius * r_speed) / self.diameter)
        self.orientation += rotation
        avg_velocity = (self.radius * r_speed + self.radius * l_speed) / 2
        translation = _2d_rotate((0, avg_velocity), self.orientation + rotation)

        # Move in the world if allowed
        self.position = self.world.get_movement_result(self.position, translation, self.diameter)

    def find_nearest_worldobject(self):
        lowest_distance = float("inf")
        nearest_worldobject = None
        for key, worldobject in self.world.objects.items():
            dist = _2d_distance_squared(self.position, worldobject.position)
            if dist < lowest_distance:
                lowest_distance = dist
                nearest_worldobject = worldobject
        return nearest_worldobject

    def handle_actions(self, nearest_worldobject):
        # Charge if action requested and not discharged (Though can we allow charging while discharged?
        # If so, it can recharge from zero anyway)
        if self.datatargets['action_charge'] >= 1:
            self.datatargets['action_charge'] = 0
            if hasattr(nearest_worldobject, 'action_charge'):
                cando, delta_energy = nearest_worldobject.action_charge()
                if cando:
                    self.energy = min(self.energy + delta_energy, 1.0)
                    self.datatarget_feedback['action_charge'] = 1
                    logging.getLogger("agent.%s" % self.uid).debug("Robot charged energy: +%f" % delta_energy)
                else:
                    self.datatarget_feedback['action_charge'] = 0
            else:
                self.datatarget_feedback['action_charge'] = 0

    def update_energy_costs(self):
        # Basic upkeep cost
        self.energy -= 0.002

        # Additional cost if movement was attempted
        # Even if the robot had no energy to move, attempting movement could still cost minimal energy.
        # If you prefer to not charge for movement when energy=0, handle condition here.
        if not self.is_discharged:
            ground_type_index = self.world.get_ground_at(self.position[0], self.position[1])
            efficiency = ground_types[ground_type_index]['move_efficiency']
            # A simple formula: harder terrain costs more energy
            self.energy -= (0.01 * (2 - efficiency))

        if self.energy < 0:
            self.energy = 0

    def is_discharged(self):
        return self.is_discharged


def _2d_rotate(position, angle_degrees):
    """rotate a 2d vector around an angle (in degrees)"""
    radians = math.radians(angle_degrees)
    # take the negative of the angle because the orientation circle works clockwise in this world
    cos = math.cos(-radians)
    sin = math.sin(-radians)
    x, y = position
    return x * cos - y * sin, - (x * sin + y * cos)


def _2d_distance_squared(position1, position2):
    """calculate the square of the distance bwtween two 2D coordinate tuples"""
    return (position1[0] - position2[0]) ** 2 + (position1[1] - position2[1]) ** 2


def _2d_translate(position1, position2):
    """add two 2d vectors"""
    return (position1[0] + position2[0], position1[1] + position2[1])


def _2d_vector_norm(vector):
    """Calculates the length /norm of a given vector."""
    return math.sqrt(sum(i**2 for i in vector))


# the indices of ground types correspond to the color numbers in the groundmap png
ground_types = (
    {
        'type': 'grass',
        'move_efficiency': 1.0,
        'agent_allowed': True,
    },
    {
        'type': 'sand',
        'move_efficiency': 1.0,
        'agent_allowed': True,
    },
    {
        'type': 'swamp',
        'move_efficiency': 0.5,
        'agent_allowed': True,
    },
    {
        'type': 'darkgrass',
        'move_efficiency': 1.0,
        'agent_allowed': True,
    },
    {
        'type': 'shallowwater',
        'move_efficiency': 0.2,
        'agent_allowed': True,
    },
    {
        'type': 'rock',
        'move_efficiency': 1.0,
        'agent_allowed': True,
    },
    {
        'type': 'clay',
        'move_efficiency': 0.7,
        'agent_allowed': True,
    },
    {
        'type': 'water',
        'move_efficiency': 0.0,
        'agent_allowed': False,
    },
    {
        'type': 'cliff',
        'move_efficiency': 1.0,
        'agent_allowed': False,
        }

)
