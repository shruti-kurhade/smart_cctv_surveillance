import time

# =========================================
# TIME LIMITS
# =========================================

ZONE_TIMERS = {

    "vault": 10,
    "atm": 20,
    "restricted": 30,
    "gate": 45,
    "parking": 90,
    "public": 120
}

# =========================================
# MOVEMENT LIMITS
# =========================================

MOVEMENT_LIMITS = {

    "vault": 5,
    "atm": 8,
    "restricted": 10,
    "gate": 15,
    "parking": 20,
    "public": 25
}

# =========================================
# LOITERING DETECTION
# =========================================

def check_loitering(obj_data):

    duration = (
        time.time()
        - obj_data["start_time"]
    )

    movement = obj_data["movement"]

    zone = obj_data.get(
        "zone",
        "public"
    )

    allowed_time = ZONE_TIMERS.get(
        zone,
        60
    )

    allowed_movement = MOVEMENT_LIMITS.get(
        zone,
        10
    )

    is_loitering = (

        duration > allowed_time
        and movement < allowed_movement

    )

    return is_loitering, duration