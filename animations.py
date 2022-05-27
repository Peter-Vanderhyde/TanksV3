tank_animation = {
    "indexes":["barrel", "body"],
    "idle barrel":{
        "duration":0,
        "loop":False,
        "initial_frame":{
            "barrel":{
                "image":"0"
            }
        }
    },
    "shoot barrel":{
        "duration":0.2,
        "loop":False,
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

animations = {
    "tank":tank_animation
}