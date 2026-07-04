import math

class BagTracker:

    def __init__(self):

        self.bags = {}
        self.next_id = 0

    def update(self, detections):

        updated = {}

        for det in detections:

            x1, y1, x2, y2 = det

            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            matched_id = None

            for bag_id, data in self.bags.items():

                bx, by = data["center"]

                distance = math.hypot(
                    cx - bx,
                    cy - by
                )

                if distance < 60:

                    matched_id = bag_id
                    break

            if matched_id is None:

                matched_id = self.next_id
                self.next_id += 1

            updated[matched_id] = {

                "center": (cx, cy)
            }

        self.bags = updated

        return self.bags