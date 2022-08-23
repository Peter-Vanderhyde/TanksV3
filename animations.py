import json
# Animation set properties:
# - indexes
# - <animation>
#
# Animation properties
# - loop
# - on finish
# - initial frame
# - frames
# 
# Possible on finish actions:
# ----------------------------------
# destroy component
# spawn tank particles
#TODO Change it so it can do things on whatever frame it wants to

animations = {
    "player tank":"player_tank_animation.json",
    "enemy tank":"player_tank_animation.json",
    "particle":"particle_animation.json",
    "bullet":"bullet_animation.json",
    "effects":"effects_animation.json"
}

def load_animations(path):
    for anim_name, anim_path in animations.items():
        with open(path + anim_path) as f:
            animations[anim_name] = json.load(f)

def format_animations():
    """This formats incomplete animations. Sometimes animations use the 'create frames' property
    to automatically make the frames property. This can be used if all of the images use numbers for
    the images. It will automatically iterate over each number and equally spread out the delay for the duration."""

    for animation_sets in animations.values():
        for animation in animation_sets:
            if animation != "indexes" and "create frames" in animation_sets[animation]\
                    and "frames" not in animation_sets[animation]:
                animation = animation_sets[animation]
                animation["frames"] = []
                image_amounts = []
                for image, props in animation["create frames"]["properties"].items():
                    image_amounts.append(props["image"])
                largest = max(image_amounts)
                first = animation["initial frame"]
                last = animation["create frames"]["properties"]
                for i in range(largest):
                    addition = {}
                    for index, image in enumerate(animation["create frames"]["properties"]):
                        addition[image] = {}
                        for string, value in last[image].items():
                            if string == "image":
                                addition[image]["image"] = str(min(i + 1, image_amounts[index])).zfill(len(first[image]["image"]))
                            else:
                                addition[image][string] = first[image][string] + (i + 1) * (value - first[image][string]) / largest
                    animation["frames"].append({
                        "delay":1 / largest,
                        "properties":addition
                    })
                last = animation["frames"][-1]
                animation["frames"].append(last)