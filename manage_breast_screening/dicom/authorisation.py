from datetime import date

from manage_breast_screening.gateway.models import GatewayAction, GatewayActionStatus


class Authorisation:
    @staticmethod
    def authorise(source_message_id: str, oid: str) -> bool:
        """
        Check for the existence of a GatewayAction with the given source_message_id and oid, created today.
        This provides a link between the source_message_id we send to the gateway in the appointment workflow
        and the oid associated with the system assigned managed identity of the gateway stored in the Gateway model.
        """
        return GatewayAction.objects.filter(
            id=source_message_id,
            gateway__oid=oid,
            created_at__date=date.today(),
            status__in=[
                GatewayActionStatus.SENT,
                GatewayActionStatus.CONFIRMED,
            ],
        ).exists()
