import math
import time


class SimpleTracker:

    def __init__(self):

        self.objects = {}

        self.next_id = 0

    def update(self, detections):

        updated_objects = {}

        for det in detections:

            x1, y1, x2, y2 = det

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            matched_id = None

            # =====================================
            # MATCH EXISTING OBJECT
            # =====================================

            for obj_id, data in self.objects.items():

                prev_cx, prev_cy = data["center"]

                distance = math.hypot(
                    cx - prev_cx,
                    cy - prev_cy
                )

                if distance < 50:

                    matched_id = obj_id
                    break

            # =====================================
            # NEW OBJECT
            # =====================================

            if matched_id is None:

                matched_id = self.next_id

                self.next_id += 1

                updated_objects[matched_id] = {

                    "center": (cx, cy),

                    "start_time": time.time(),

                    "last_position": (cx, cy),

                    "movement": 0
                }

            # =====================================
            # EXISTING OBJECT
            # =====================================

            else:

                prev = self.objects[matched_id]

                px, py = prev["last_position"]

                # ONLY CURRENT FRAME MOVEMENT
                movement = math.hypot(
                    cx - px,
                    cy - py
                )

                updated_objects[matched_id] = {

                    "center": (cx, cy),

                    "start_time": prev["start_time"],

                    "last_position": (cx, cy),

                    "movement": movement
                }

        self.objects = updated_objects

        return self.objects