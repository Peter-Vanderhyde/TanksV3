# Animation set properties:
# - indexes
# - loop
# - on finish
# - <animation>
#
# Possible on finish actions:
# ----------------------------------
# destroy component
#TODO Change it so it can do things on whatever frame it wants to

tank_animation = {
    "indexes":["barrel", "body"],
    "spawn":{
        "duration":0.65,
        "initial_frame":{
            "barrel":{
                "scale":0
            },
            "body":{
                "scale":0
            }
        },
        "frames":[
            {
                "delay":0.4,
                "properties":{
                    "barrel":{
                        "scale":0
                    },
                    "body":{
                        "scale":1.3
                    }
                }
            },
            {
                "delay":0.1,
                "properties":{
                    "barrel":{
                        "scale":0
                    },
                    "body":{
                        "scale":1
                    }
                }
            },
            {
                "delay":0.4,
                "properties":{
                    "barrel":{
                        "scale":1.2
                    },
                    "body":{
                        "scale":1
                    }
                }
            },
            {
                "delay":0.1,
                "properties":{
                    "barrel":{
                        "scale":1
                    },
                    "body":{
                        "scale":1
                    }
                }
            }
        ]
    },
    "idle barrel":{
        "duration":0,
        "initial_frame":{
            "barrel":{
                "image":"0"
            }
        }
    },
    "shoot barrel":{
        "duration":0.2,
        "initial_frame":{
            "barrel":{
                "image":"0"
            }
        },
        "frames":[
            {
                "delay":0.25,
                "properties":{
                    "barrel":{
                        "image":"1"
                    }
                }
            },
            {
                "delay":0.25,
                "properties":{
                    "barrel":{
                        "image":"2"
                    }
                }
            },
            {
                "delay":0.25,
                "properties":{
                    "barrel":{
                        "image":"3"
                    }
                }
            },
            {
                "delay":0.25,
                "properties":{
                    "barrel":{
                        "image":"4"
                    }
                }
            }
        ]
    }
}

particle_animation = {
    "indexes":["particle"],
    "expired":{
        "duration":0.35,
        "on finish":"destroy component",
        "initial_frame":{
            "particle":{
                "scale":1
            }
        },
        "frames":[
            {
                "delay":1,
                "properties":{
                    "particle":{
                        "scale":0
                    }
                }
            }
        ]
    }
}

animations = {
    "tank":tank_animation,
    "particle":particle_animation
}