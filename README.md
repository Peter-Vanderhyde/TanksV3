# TanksV3
***Peter Vanderhyde***
<hr>

## What's New?
Well, pretty much everything! I've restarted the game from the ground up. The strictly narrow-minded OOP technique previously used for all game objects was significantly slower to run than necessary. That's why I've switched to using an ECS system.

## What's ECS?
ECS stands for Entity Component System. Instead of creating a new class for every object within the game, every object in the game is represented by a single id number. They begin as an empty shell with no functionality. To add functionality, I create components for everything. A graphics component for entities with textures, a physics component for entities that move, a collision component, an animation component, and the list goes on. Using an ECS, the game can focus on only displaying things that can be seen, moving things that can move, and so on. It's not wasting resources. These components can be mixed and matched to theoretically create any combination of components needed for any functionality.
