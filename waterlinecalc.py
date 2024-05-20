#!/opt/homebrew/bin/python3.10
from dataclasses import dataclass
from time import time, sleep
from vedo import *
import numpy as np


@dataclass
class Plane:
    origin: tuple
    normal: tuple

    def flip(self) -> float:
        return Plane(origin=self.origin, normal=tuple(-x for x in self.normal))
    

hull = Mesh('/Users/jmalle/Downloads/beamier-full-2.stl')

# this stl uses ft so need ft3 to m3
stl_unit_cubed_to_m3_conversion = 0.0283168

init_cog = hull.center_of_mass()

hull = hull.shift(-init_cog)
hull = hull.shift(np.array([0, 0, 1.5]))
waterline = Plane(origin=(0, 0, 0), normal=(0, 0, 1))

plt = Plotter(axes=True)
t0 = time()
time_step = 0.1


@dataclass
class Positions:
    position: np.array = np.array([0., 0., 0.])
    velocity: np.array = np.array([0., 0., 0.])
    angle: np.array = np.array([0., 30., 0.])
    angular_velocity: np.array = np.array([0., 0., 0.])

position = Positions()

def get_outside_inside_water(_hull):
    outside = _hull.clone().cut_with_plane(origin=waterline.origin, normal=waterline.normal)
    inside = _hull.clone().cut_with_plane(origin=waterline.origin, normal=waterline.flip().normal)
    return outside, inside

def apply_position(_hull, pos: Positions):
    shifted = _hull.clone().shift(pos.position)
    shifted = shifted.rotate_x(pos.angle[0])
    shifted = shifted.rotate_y(pos.angle[1])
    shifted = shifted.rotate_z(pos.angle[2])
    return shifted


def render():
    global plt, hull, position, t0
    plt.clear()
    pre_hull = apply_position(hull, position)
    pre_outside, pre_inside = get_outside_inside_water(pre_hull)
    cog = pre_hull.center_of_mass()
    cob = pre_inside.center_of_mass()

    
    # Plot cog and cob
    plt += [
        Point(pos=cog, r=50, c='gold'),
        Point(pos=cob, r=50, c='black')
    ]

    boat_weight = 2500 # kg
    displacement_volume = pre_inside.volume() * stl_unit_cubed_to_m3_conversion
    displaced_water_weight = displacement_volume * 997.77 # kg
    gravity = 9.8

    # prevent things from shooting around especially if initial conditions are
    # wrong
    friction_fudge_factor = 0.96 # 0.93

    # how long has it been
    time_step = time() - t0
    t0 = time()


    # Calculate the forces
    force_buoyancy = np.array([0, 0, displaced_water_weight * gravity])
    force_gravity = np.array([0, 0, -boat_weight * gravity])
    net_force = force_buoyancy + force_gravity

    # Update linear velocity and position
    acceleration = net_force / boat_weight
    position.velocity += acceleration * time_step
    position.velocity *= friction_fudge_factor
    position.position += position.velocity * time_step
    
    # Calculate the torques
    torque_buoyancy = np.cross(cob - cog, force_buoyancy)
    torque_gravity = np.cross(-cog, force_gravity)
    net_torque = torque_buoyancy + torque_gravity

    # Update angular velocity and rotation
    angular_acceleration = net_torque / boat_weight
    position.angular_velocity += angular_acceleration * time_step
    position.angular_velocity *= friction_fudge_factor
    position.angle += position.angular_velocity * time_step

    post_hull = apply_position(hull, position)
    post_outside, post_inside = get_outside_inside_water(post_hull)
    post_outside.c('brown').alpha(0.95)
    post_inside.c('blue').alpha(0.7)

    description = Text2D(f"draft: {abs(position.position[2]):.2f} ", bg='white', alpha=1)

    # Render the updated scene
    plt += [post_outside, post_inside, description]
    plt.render()
    # sleep(time_step)


render()

def loop_func(event):
    render()

plt.add_callback("timer", loop_func)
plt.timer_callback("start")
plt.show(camera=dict(
    pos=(0, -100, 14), # back view
    # pos=(100, 12, 4), # side view
    focalPoint=(0, 6, 4), # Focal point (where the camera is looking)
    viewup=(0, 0, 1),     # The view-up vector (defining the up direction for the camera)
))
plt.close()


# hull_outside_water.c('brown').lighting('glossy').alpha(1.0)

# # hull_inside_water = split(hull, waterline.flip())
# # hull_inside_water.c('brown').lighting('glossy').alpha(1.0)

# # Define the camera position and focal point
# camera = 

# # Show everything with the specified camera settings
# show(hull_outside_water, camera=camera, axes=True)