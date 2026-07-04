import math
import time

abandoned_registry = {}

ABANDON_TIME = 10
DISTANCE_LIMIT = 200


def check_abandoned_object(
        bag_id,
        bag_center,
        persons):

    current_time = time.time()

    bx, by = bag_center

    nearest_distance = 999999

    nearest_person = None

    for person_id, pdata in persons.items():

        px, py = pdata["center"]

        distance = math.hypot(
            bx - px,
            by - py
        )

        if distance < nearest_distance:

            nearest_distance = distance
            nearest_person = person_id

    if bag_id not in abandoned_registry:

        abandoned_registry[bag_id] = {

            "owner": nearest_person,
            "start_time": current_time
        }

        return False

    owner = abandoned_registry[bag_id]["owner"]

    owner_distance = 999999

    if owner in persons:

        px, py = persons[owner]["center"]

        owner_distance = math.hypot(
            bx - px,
            by - py
        )

    if owner_distance > DISTANCE_LIMIT:

        duration = (
            current_time
            - abandoned_registry[bag_id]["start_time"]
        )

        if duration > ABANDON_TIME:

            return True

    else:

        abandoned_registry[bag_id][
            "start_time"
        ] = current_time

    return False