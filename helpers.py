import random
from pygame.math import Vector2
import settings

def spawn_particles(component, amount, particles, spawn_point, rotation, scale, speed, lifetime, spin_rate=0, decel=0.07, spin_friction=True, friction=settings.PARTICLE_FRICTION):
    game = component.game
    parent_entity_id = component.collision_id
    owner_string = game.get_component(parent_entity_id, 'barrel manager').owner_string
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
        
        particle = random.choice(particles)
        game.add_action(game.actions.SpawnParticle(game.get_unique_id(),
            f"{particle}_{owner_string}", *new_args))