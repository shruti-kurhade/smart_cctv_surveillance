from ultralytics import YOLO
import cv2
import time
import os
from datetime import datetime

from zones import RESTRICTED_ZONES, is_in_zone
from tracker import SimpleTracker
from loitering import check_loitering
from risk_engine import compute_risk
from fight_detection import detect_fight

from bag_tracker import BagTracker
from object_left import (check_abandoned_object)
# =========================================
# GLOBAL VARIABLES
# =========================================

last_alarm_time = 0
last_loitering_alert = 0
last_fight_alert = 0
last_object_alert=0
# =========================================
# LOAD MODEL
# =========================================

model = YOLO("yolov8s.pt")
weapon_model =YOLO("models/weapon_model.pt")

# =========================================
# TRACKER
# =========================================

tracker = SimpleTracker()
bag_tracker = BagTracker()

# =========================================
# SAVE EVIDENCE
# =========================================

def save_evidence(frame, label):

    os.makedirs(
        "evidence/incidents",
        exist_ok=True
    )

    os.makedirs(
        "logs",
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"evidence/incidents/"
        f"{label}_{timestamp}.jpg"
    )

    cv2.imwrite(
        filename,
        frame
    )

    with open(
        "logs/incidents.txt",
        "a"
    ) as f:

        f.write(
            f"{timestamp} : "
            f"{label} detected\n"
        )

# =========================================
# MAIN DETECTION FUNCTION
# =========================================

def detect(frame):

    global last_alarm_time
    global last_loitering_alert
    global last_fight_alert
    global last_object_alert

    alarm_triggered = False
    alert_type = None
    # =====================================
    # YOLO DETECTION
    # =====================================

    results = model(frame)[0]

    detections = []
    bag_detections = []

    weapon_classes = [
        "knife",
        "pistol",
        "handgun",
        "rifle",
        "shotgun"
    ]
    
    # =====================================
    # OBJECT DETECTION LOOP
    # =====================================
    
    for box in results.boxes:

        x1, y1, x2, y2 = map(
            int,
            box.xyxy[0]
        )

        cls = int(box.cls[0])

        label = model.names[cls].lower()

        conf = float(box.conf[0])

        if conf < 0.5:
            continue

        color = (0, 255, 0)

        # =====================================
        # PERSON DETECTION
        # =====================================

        if label == "person":

            detections.append(
                (x1, y1, x2, y2)
            )
        
        if label in [
            "backpack","handbag","suitcase"
            ]:
            bag_detections.append((x1,y1,x2,y2))

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            f"{label} {conf:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )    

        # =====================================
        # WEAPON DETECTION
        # =====================================

        if label in weapon_classes:

            color = (0, 0, 255)

            cv2.putText(
                frame,
                f"WEAPON: {label}",
                (x1, y1 - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )

            current_time = time.time()

            if current_time - last_alarm_time > 5:


                alarm_triggered = True
                alert_type = "weapon"

                last_alarm_time = current_time

                print(
                    f"🚨 WEAPON ALERT: {label}"
                )

                save_evidence(
                    frame,
                    label
                )

        # =====================================
        # DRAW OBJECT BOX
        # =====================================

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            f"{label} {conf:.2f}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2
        )

    # =====================================
    # TRACKING UPDATE
    # =====================================

    tracked_objects = tracker.update(
        detections
    )
    
    tracked_bags = bag_tracker.update(bag_detections)
    # =====================================
    # FIGHT DETECTION
    # =====================================

    fight_detected = detect_fight(
        tracked_objects
    )

    current_time = time.time()

    if (
        fight_detected
        and current_time - last_fight_alert > 8
    ):

        alarm_triggered = True
        alert_type = "fight"

        last_fight_alert = current_time

        # RED BORDER

        cv2.rectangle(
            frame,
            (0, 0),
            (frame.shape[1], frame.shape[0]),
            (0, 0, 255),
            8
        )

        cv2.putText(
            frame,
            "FIGHT DETECTED",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )

        print("🚨 FIGHT DETECTED")

        save_evidence(
            frame,
            "fight"
        )
    
    for bag_id, bag in tracked_bags.items():
        abandoned = check_abandoned_object(bag_id,bag["center"],tracked_objects)
        if abandoned:
            current_time=time.time()
            if(current_time-last_object_alert>10):
                last_object_alert=current_time
                alarm_triggered=True
                alert_type = "abandoned"
                
                bx,by=bag["center"]
                cv2.putText(frame,"ABANDONED OBJECT",(bx-80,by-20),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),2)
                print("ABANDONED OBJECT")
                save_evidence(frame,"abandoned_object")
    # =====================================
    # DRAW RESTRICTED ZONES
    # =====================================

    for zone in RESTRICTED_ZONES:

        zx1, zy1, zx2, zy2 = zone

        cv2.rectangle(
            frame,
            (zx1, zy1),
            (zx2, zy2),
            (255, 0, 0),
            2
        )

        cv2.putText(
            frame,
            "Restricted Zone",
            (zx1, zy1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

    # =====================================
    # PERSON ANALYSIS
    # =====================================

    for obj_id, data in tracked_objects.items():

        cx, cy = data["center"]

        x1 = cx - 50
        y1 = cy - 100
        x2 = cx + 50
        y2 = cy + 100

        # =====================================
        # RESTRICTED ZONE CHECK
        # =====================================

        in_zone = any(

            is_in_zone(
                cx,
                cy,
                cx,
                cy,
                zone
            )

            for zone in RESTRICTED_ZONES
        )

        # =====================================
        # SET ZONE TYPE
        # =====================================

        if in_zone:
            data["zone"] = "restricted"
        else:
            data["zone"] = "public"

        # =====================================
        # LOITERING CHECK
        # =====================================

        loitering, duration = check_loitering(
            data
        )

        color = (0, 255, 0)

        current_time = time.time()

        # =====================================
        # LOITERING ALERT
        # =====================================

        if (
            in_zone
            and loitering
            and current_time - last_loitering_alert > 10
        ):

            color = (0, 0, 255)

            alarm_triggered = True
            alert_type = "loitering"

            last_loitering_alert = current_time

            cv2.putText(
                frame,
                "SUSPICIOUS LOITERING",
                (x1, y1 - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

            print(
                f"🚨 LOITERING ALERT: ID {obj_id}"
            )

            save_evidence(
                frame,
                "loitering"
            )

        # =====================================
        # PERSON BOX
        # =====================================

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            color,
            2
        )

        cv2.putText(
            frame,
            f"ID:{obj_id}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

        cv2.putText(
            frame,
            f"Time:{duration:.1f}s",
            (x1, y2 + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    return frame, alarm_triggered, alert_type