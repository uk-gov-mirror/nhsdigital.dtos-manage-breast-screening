from manage_breast_screening.core.feature_flags import FeatureFlag
from manage_breast_screening.gateway.models import Relay


def gateway_images_enabled(appointment):
    """Check if automatic gateway image retrieval is enabled."""
    if FeatureFlag.is_enabled("gateway_images"):
        return Relay.for_appointment(appointment) is not None
    return False
