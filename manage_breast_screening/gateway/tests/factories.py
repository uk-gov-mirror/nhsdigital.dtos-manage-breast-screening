from factory.declarations import Sequence, SubFactory
from factory.django import DjangoModelFactory

from .. import models


class GatewayFactory(DjangoModelFactory):
    class Meta:
        model = models.Gateway

    name = Sequence(lambda n: f"Gateway {n}")
    description = Sequence(lambda n: f"Description for Gateway {n}")
    oid = Sequence(lambda n: f"00000000-0000-0000-0000-{n:012d}")
    resource_name = Sequence(lambda n: f"gateway-resource-{n}")


class GatewayActionFactory(DjangoModelFactory):
    class Meta:
        model = models.GatewayAction

    appointment = SubFactory(
        "manage_breast_screening.participants.tests.factories.AppointmentFactory"
    )
    type = models.GatewayActionType.WORKLIST_CREATE
    payload = {}
    status = models.GatewayActionStatus.PENDING
    accession_number = Sequence(lambda n: f"ACC20240601{n:04d}")
    sent_at = None
    gateway = SubFactory(GatewayFactory)


class RelayFactory(DjangoModelFactory):
    class Meta:
        model = models.Relay

    namespace = Sequence(lambda n: f"myrelay{n}.servicebus.windows.net")
    hybrid_connection_name = Sequence(lambda n: f"hybrid-connection-{n}")
    key_name = "RootManageSharedAccessKey"
    shared_access_key_variable_name = Sequence(lambda n: f"SHARED_ACCESS_KEY_{n}")
    setting = SubFactory(
        "manage_breast_screening.clinics.tests.factories.SettingFactory"
    )
    gateway = SubFactory(GatewayFactory)
