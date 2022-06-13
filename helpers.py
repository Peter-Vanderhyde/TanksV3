import random
from pygame.math import Vector2
import settings

def spawn_shapes(game, amount, spawn_range):
    for i in range(amount):
        spawn = Vector2(random.randint(spawn_range[0][0], spawn_range[1][0]), random.randint(spawn_range[0][1], spawn_range[1][1]))
        id = game.get_unique_id()
        rotation = random.uniform(0, 360)
        scale = 1
        xp = 10
        spin_rate = 5
        spin_friction = False
        game.add_action(game.actions.SpawnShape(id, spawn, rotation, scale, xp, spin_rate, spin_friction))

def spawn_particles(component, amount, source_string, spawn_point, rotation, scale, speed, lifetime, spin_rate=0, decel=0.07, spin_friction=True, friction=settings.PARTICLE_FRICTION):
    game = component.game
    args = [spawn_point, rotation, scale, [speed, speed, 0], decel, lifetime, spin_rate, spin_friction, friction]
    for i in range(amount):
        new_args = []
        for arg in args:
            if type(arg) == list:
                if arg == [speed, speed, 0]:
                    if type(speed) == list:
                        s = random.uniform(*speed)
                        new_args.append([s, s, 0])
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(random.uniform(*arg))
            else:
                new_args.append(arg)
        
        particles = settings.PARTICLES[source_string]
        particle = random.choice(particles)
        game.add_action(game.actions.SpawnParticle(game.get_unique_id(),
            f"{particle}", *new_args))

def handle_collision(component_a, component_b):
    parent_b_id = component_b.collision_id
    game = component_a.game
    if component_a.collision_category == "projectiles":
        if component_b.collision_category == "actors":
            particle_num = 6
            transform = component_a.transform_component
            game.helpers.spawn_particles(component_a,
                particle_num,
                component_a.particle_source_name,
                lifetime=[3, 5],
                spawn_point=Vector2(transform.x, transform.y),
                rotation=[0, 360],
                scale=1,
                speed=[100, 200],
                spin_rate=[10, 20])
            damage = game.get_property(component_a.id, "damage")
            game.add_action(game.actions.Damage(parent_b_id, damage))
            game.add_action(game.actions.Destroy(component_a.id))
            if game.get_property(component_b.id, "health") - damage <= 0:
                if game.camera.target_id == component_b.collision_id:
                    game.add_action(game.actions.FocusCamera(component_a.collision_id))
                game.get_component(component_b.id, "animator").play("die")
                game.add_action(game.actions.StopFiringBarrels(component_b.id))
                component_b.inactive = True
                transform = game.get_component(parent_b_id, "transform")
                
        elif component_b.collision_category in ["projectiles", "shapes"]:
            particle_num = 6
            transform = component_a.transform_component
            game.helpers.spawn_particles(component_a, particle_num,
                component_a.particle_source_name,
                lifetime=[3, 5],
                spawn_point=Vector2(transform.x, transform.y),
                rotation=[transform.rotation - 40, transform.rotation + 40],
                scale=1,
                speed=[100, 200],
                spin_rate=[10, 20])
            game.add_action(game.actions.Destroy(component_a.id))