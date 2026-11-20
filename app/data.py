"""Fake demo data. Nothing here is real: no real customers, codes or secrets."""

# Pickup codes are six digits. The demo code for L-1042 is deliberately low
# so the break-mode attack finds it within seconds; real codes are random.
PICKUP_CODES: dict[str, str] = {
    "L-1042": "000137",
    "L-2001": "583920",
}
