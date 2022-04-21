# TanksV3
 I am restarting my tank game with a whole new method to the madness. I am trying to implement my game using an ECS (Entity Component System) model instead of the strictly object oriented approach I've been using. Before, every object was its own class. A shape was a class, a bullet was a class, etc. This time, I'm using the entities approach where you create an entity, which is in essence an empty shell. You then fill that shell with the different components that the entity will be using. For example, a shape would simply be an entity with a positional component, a graphical component, and a collision component. Particles would be the same, but without the collision aspect. Missiles would require some kind of AI component, and so on. This is how you can build an entity up using components to be capable of whatever you want. That way you can reuse those components for other entities that could use them in the future.
