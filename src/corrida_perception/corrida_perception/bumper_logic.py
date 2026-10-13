"""Pure Python logic for identifying Create 3 bumper detections."""

BUMP = 1


def get_bumper_names(message):
    """Return the frame IDs of all bumper detections in a hazard message."""
    return [
        detection.header.frame_id
        for detection in message.detections
        if detection.type == BUMP
        and detection.header.frame_id.startswith("bump_")
    ]
