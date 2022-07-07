import random
from pygame.math import Vector2
import settings
import pygame

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

def spawn_particles(component, amount, source_string, spawn_point, rotation, scale, speed, lifetime, spin_rate=0, decel=0.07, spin_friction=True, friction=settings.PARTICLE_FRICTION, collide=False):
    game = component.game
    args = [spawn_point, rotation, scale, [speed, speed, 0], decel, lifetime, spin_rate, spin_friction, friction, collide]
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
            game.get_component(component_a.id, "animator").play("collided")
            damage = game.get_property(component_a.id, "damage")
            game.add_action(game.actions.Damage(parent_b_id, damage))
            if game.get_property(component_b.id, "health") - damage <= 0:
                game.set_property(component_b.id, "health", 0)
                if game.camera.target_id == component_b.collision_id:
                    game.add_action(game.actions.FocusCamera(component_a.collision_id))
                
                game.get_component(component_b.id, "animator").play("die")
                game.add_action(game.actions.StopFiringBarrels(component_b.id))
                component_b.inactive = True
                
        elif component_b.collision_category in ["projectiles", "shapes"]:
            game.get_component(component_a.id, "animator").play("collided")
    
    elif component_a.collision_category == "actors":
        if component_b.collision_category == "particles":
            game.add_action(game.actions.Destroy(component_b.id))
            game.set_property(component_a.id, "health", min(game.get_property(component_a.id, "health") + 2, 100))

def tank_death(component):
    collider = component.game.get_component(component.id, "collider")
    transform = component.game.get_component(component.id, "transform")
    component.game.helpers.spawn_particles(collider,
        20,
        collider.particle_source_name,
        lifetime=[5, 10],
        spawn_point=Vector2(transform.x, transform.y),
        rotation=[0, 360],
        scale=[1, 1.5],
        speed=[50, 500],
        spin_rate=[10, 50],
        collide=True)
    component.game.helpers.spawn_particles(collider,
        1,
        "barrel",
        lifetime=[5, 10],
        spawn_point=Vector2(transform.x, transform.y),
        rotation=transform.rotation,
        scale=1,
        speed=[200, 500],
        spin_rate=[10, 50])

def bullet_death(component):
    collider = component.game.get_component(component.id, "collider")
    transform = component.game.get_component(component.id, "transform")
    spawn_particles(collider,
        2,
        collider.particle_source_name,
        lifetime=[3, 5],
        spawn_point=Vector2(transform.x, transform.y),
        rotation=[transform.rotation - 40, transform.rotation + 40],
        scale=1,
        speed=[100, 200],
        spin_rate=[10, 20])

def create_font(name, size):
    font = pygame.font.SysFont(name, size)
    return font

def render_font(font, text, color):
    font = font.render(text, False, color)
    rect = font.get_rect()
    return font, rect