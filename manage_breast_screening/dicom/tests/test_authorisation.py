import uuid
from datetime import date, timedelta

import pytest

from manage_breast_screening.gateway.models import GatewayActionStatus
from manage_breast_screening.gateway.tests.factories import (
    GatewayActionFactory,
    GatewayFactory,
)

from ..authorisation import Authorisation


@pytest.mark.django_db
class TestAuthorisation:
    def test_authorisation(self):
        source_message_id = str(uuid.uuid4())
        oid = str(uuid.uuid4())
        GatewayActionFactory(
            id=source_message_id,
            gateway=GatewayFactory(oid=oid),
            created_at=date.today(),
            status=GatewayActionStatus.SENT,
        )

        assert Authorisation.authorise(source_message_id, oid) is True

    def test_authorisation_no_action(self):
        source_message_id = str(uuid.uuid4())
        oid = str(uuid.uuid4())

        assert Authorisation.authorise(source_message_id, oid) is False

    def test_authorisation_wrong_status(self):
        source_message_id = str(uuid.uuid4())
        oid = str(uuid.uuid4())
        GatewayActionFactory(
            id=source_message_id,
            gateway=GatewayFactory(oid=oid),
            created_at=date.today(),
            status=GatewayActionStatus.PENDING,
        )

        assert Authorisation.authorise(source_message_id, oid) is False

    def test_authorisation_old_action(self):
        source_message_id = str(uuid.uuid4())
        oid = str(uuid.uuid4())
        action = GatewayActionFactory(
            id=source_message_id,
            gateway=GatewayFactory(oid=oid),
            status=GatewayActionStatus.SENT,
        )
        action.created_at = date.today() - timedelta(days=1)
        action.save()

        assert Authorisation.authorise(source_message_id, oid) is False

    def test_authorisation_wrong_oid(self):
        source_message_id = str(uuid.uuid4())
        oid = str(uuid.uuid4())
        GatewayActionFactory(
            id=source_message_id,
            gateway=GatewayFactory(oid=str(uuid.uuid4())),
            created_at=date.today(),
            status=GatewayActionStatus.SENT,
        )

        assert Authorisation.authorise(source_message_id, oid) is False

    def test_authorisation_no_gateway(self):
        source_message_id = str(uuid.uuid4())
        oid = str(uuid.uuid4())
        GatewayActionFactory(
            id=source_message_id,
            gateway=None,
            created_at=date.today(),
            status=GatewayActionStatus.SENT,
        )

        assert Authorisation.authorise(source_message_id, oid) is False

    def test_bypass_authorisation(self, monkeypatch):
        source_message_id = str(uuid.uuid4())
        oid = str(uuid.uuid4())
        monkeypatch.setenv("BYPASS_API_AUTHORISATION", "true")

        assert Authorisation.authorise(source_message_id, oid) is True
