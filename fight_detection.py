import math

# =========================================
# FIGHT DETECTION FUNCTION
# =========================================

def detect_fight(tracked_objects):

    object_ids = list(
        tracked_objects.keys()
    )

    # Need at least 2 people
    if len(object_ids) < 2:
        return False

    # =====================================
    # CHECK EVERY PAIR
    # =====================================

    for i in range(len(object_ids)):

        for j in range(i + 1, len(object_ids)):

            obj1 = tracked_objects[
                object_ids[i]
            ]

            obj2 = tracked_objects[
                object_ids[j]
            ]

            # Centers
            x1, y1 = obj1["center"]
            x2, y2 = obj2["center"]

            # =====================================
            # DISTANCE
            # =====================================

            distance = math.hypot(
                x1 - x2,
                y1 - y2
            )

            # =====================================
            # MOVEMENT SPEED
            # =====================================

            movement1 = obj1["movement"]
            movement2 = obj2["movement"]

            print(
                "Distance:",
                round(distance, 2),
                "Move1:",
                round(movement1, 2),
                "Move2:",
                round(movement2, 2)
            )

            # =====================================
            # FIGHT CONDITIONS
            # =====================================

            if (

                distance < 250
                and movement1 > 8
                and movement2 > 8

            ):

                return True

    return False