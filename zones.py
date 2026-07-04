# Restricted zones
# (x1, y1, x2, y2)

RESTRICTED_ZONES = [

    (100, 100, 400, 400),

]

def is_in_zone(x1, y1, x2, y2, zone):

    zx1, zy1, zx2, zy2 = zone

    cx = int((x1 + x2) / 2)

    cy = int((y1 + y2) / 2)

    return (
        zx1 < cx < zx2
        and
        zy1 < cy < zy2
    )
