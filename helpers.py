import random
from pygame.math import Vector2

def spawn_particles(component, amount, particles, scale_range, rotation_range):
    game = component.game
    transform = game.get_component(component.id, "transform")
    parent_entity_id = component.collision_id
    owner_string = game.get_component(parent_entity_id, 'barrel manager').owner_string
    for i in range(amount):
        particle = random.choice(particles)
        scale = random.uniform(*scale_range)
        decel = (scale - 0.5) / 0.7 * 0.1
        game.add_action(game.actions.SpawnParticle(game.get_unique_id(),
            f"{particle}_{owner_string}",
            Vector2(transform.x, transform.y),
            random.uniform(*rotation_range),
            scale,
            [400, random.randint(100, 300), 0],
            decel,
            random.uniform(3.0, 5.0)))