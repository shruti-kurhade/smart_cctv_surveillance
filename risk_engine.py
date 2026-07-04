def compute_risk(label, in_zone):

    risk = 0.1

    # Person in restricted area
    if label == "person" and in_zone:
        risk += 0.5

    # Weapon detection
    if label in [
        "pistol",
        "knife",
        "rifle",
        "shotgun"
    ]:
        risk = 1.0

    # Fire risk
    if label in ["fire", "smoke"]:
        risk = 1.0

    return min(risk, 1.0)
