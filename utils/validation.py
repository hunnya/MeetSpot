"""Input validation routines for MeetSpot."""
from typing import List, Dict, Tuple


def validate_coordinates(lat: float, lon: float) -> bool:
    """Checks whether latitude and longitude values fall within standard geographic limits."""
    try:
        lat = float(lat)
        lon = float(lon)
        return -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0
    except (ValueError, TypeError):
        return False


def validate_participants(participants: List[Dict[str, str]]) -> Tuple[bool, str]:
    """Validates participant names and addresses before calculation."""
    if not participants or len(participants) < 2:
        return False, "At least 2 participants are required to find a fair meeting point."

    if len(participants) > 10:
        return False, "MeetSpot supports up to 10 participants per meeting."

    names = []
    addresses = []
    for idx, p in enumerate(participants, start=1):
        name = p.get("name", "").strip()
        address = p.get("address", "").strip()

        if not name:
            return False, f"Participant {idx} is missing a name."
        if not address:
            return False, f"Please enter a starting location for {name}."

        names.append(name.lower())
        addresses.append(address.lower())

    if len(set(names)) < len(names):
        return False, "Participant names should be unique so everyone can be identified."

    return True, ""
