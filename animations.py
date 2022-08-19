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

tank_animation = {
    "indexes":["barrel", "body"],
    "spawn":{
        "duration":0.65,
        "initial frame":{
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
                    "body":{
                        "scale":1.3
                    }
                }
            },
            {
                "delay":0.1,
                "properties":{
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
                    }
                }
            },
            {
                "delay":0.1,
                "properties":{
                    "barrel":{
                        "scale":1
                    }
                }
            }
        ]
    },
    "die":{
        "duration":0.4,
        "on finish":["destroy component", "spawn tank particles"],
        "initial frame":{
            "barrel":{
                "scale":1
            },
            "body":{
                "scale":1
            }
        },
        "frames":[
            {
                "delay":0.4,
                "properties":{
                    "barrel":{
                        "scale":0.6
                    },
                    "body":{
                        "scale":0.6
                    }
                }
            },
            {
                "delay":0.1,
                "properties":{
                    "barrel":{
                        "scale":0.6
                    },
                    "body":{
                        "scale":0.6
                    }
                }
            },
            {
                "delay":0.5,
                "properties":{
                    "barrel":{
                        "scale":1.5
                    },
                    "body":{
                        "scale":1.5
                    },
                    "sound":{
                        "name":"pop_low"
                    }
                }
            }
        ]
    },
    "idle barrel":{
        "duration":0,
        "initial frame":{
            "barrel":{
                "image":"0"
            }
        }
    },
    "shoot barrel":{
        "duration":1,
        "initial frame":{
            "barrel":{
                "image":"0"
            },
            "sound":{
                "name":"pop_high",
                "volume":0.3
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
        "on finish":["destroy component"],
        "initial frame":{
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

bullet_animation = {
    "indexes":["bullet"],
    "collided":{
        "duration":0,
        "on finish":["destroy component", "spawn bullet particles"],
        "initial frame":{
            "bullet":{
                "scale":1
            }
        }
    },
    "expired":{
        "duration":0.3,
        "on finish":["destroy component"],
        "initial frame":{
            "bullet":{
                "scale":1
            }
        },
        "frames":[
            {
                "delay":1,
                "properties":{
                    "bullet":{
                        "scale":0
                    }
                }
            }
        ]
    }
}

animations = {
    "tank":tank_animation,
    "particle":particle_animation,
    "bullet":bullet_animation
}