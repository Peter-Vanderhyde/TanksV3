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

player_tank_animation = {
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
        "custom frames":[
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
        "custom frames":[
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
        "custom frames":[
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
    },
    "healing":{
        "duration":0.25,
        "initial frame":{
            "body":{
                "image":"healing"
            }
        },
        "custom frames":[
            {
                "delay":1,
                "properties":{
                    "body":{
                        "image":"normal"
                    }
                }
            }
        ]
    },
    "damaged":{
        "duration":0.25,
        "initial frame":{
            "body":{
                "image":"damaged"
            }
        },
        "custom frames":[
            {
                "delay":1,
                "properties":{
                    "body":{
                        "image":"normal"
                    }
                }
            }
        ]
    }
}

enemy_tank_animation = player_tank_animation

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
        "custom frames":[
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
        "custom frames":[
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

effects_animation = {
    "indexes":["effect"],
    "collected experience":{
        "duration":0.5,
        "on finish":["destroy component"],
        "initial frame":{
            "effect":{
                "image":0,
                "scale":1
            }
        },
        "custom frames":[
            {
                "delay":0.2,
                "properties":{
                    "effect":{
                        "image":"1",
                        "scale":1.1
                    }
                }
            },
            {
                "delay":0.2,
                "properties":{
                    "effect":{
                        "image":"2",
                        "scale":1.2
                    }
                }
            },
            {
                "delay":0.2,
                "properties":{
                    "effect":{
                        "image":"3",
                        "scale":1.3
                    }
                }
            },
            {
                "delay":0.2,
                "properties":{
                    "effect":{
                        "image":"4",
                        "scale":1.4
                    }
                }
            },
            {
                "delay":0.2,
                "properties":{
                    "effect":{
                        "image":"4",
                        "scale":1.5
                    }
                }
            }
        ]
    },
    "healing plus":{
        "duration":0.25,
        "on finish":["destroy component"],
        "initial frame":{
            "effect":{
                "image":"healing_plus",
                "scale":0
            }
        },
        "custom frames":[
            {
                "delay":0.1,
                "properties":{
                    "effect":{
                        "scale":1
                    }
                }
            },
            {
                "delay":0.8,
                "properties":{
                    "effect":{
                        "scale":1
                    }
                }
            },
            {
                "delay":0.1,
                "properties":{
                    "effect":{
                        "scale":0
                    }
                }
            }
        ]
    },
    "spawn wave":{
        "duration":0.75,
        "on finish":["destroy component"],
        "initial frame":{
            "effect":{
                "image":"wave_1",
                "scale":1
            }
        },
        "custom frames":[
            {
                "delay":0.15,
                "properties":{
                    "effect":{
                        "image":"wave_2",
                        "scale":1.3
                    }
                }
            },
            {
                "delay":0.15,
                "properties":{
                    "effect":{
                        "image":"wave_3",
                        "scale":1.55
                    }
                }
            },
            {
                "delay":0.15,
                "properties":{
                    "effect":{
                        "image":"wave_4",
                        "scale":1.75
                    }
                }
            },
            {
                "delay":0.15,
                "properties":{
                    "effect":{
                        "image":"wave_5",
                        "scale":1.9
                    }
                }
            },
            {
                "delay":0.15,
                "properties":{
                    "effect":{
                        "image":"wave_5",
                        "scale":2
                    }
                }
            },
        ]
    },
    "vortex":{
        "duration":1.5,
        "on finish":["destroy component"],
        "initial frame":{
            "effect":{
                "image":"00"
            }
        },
        "piskel frames":{
            "effect":{
                "image":"16"
            }
        }
    }
}

animations = {
    "player tank":player_tank_animation,
    "enemy tank":enemy_tank_animation,
    "particle":particle_animation,
    "bullet":bullet_animation,
    "effects":effects_animation
}