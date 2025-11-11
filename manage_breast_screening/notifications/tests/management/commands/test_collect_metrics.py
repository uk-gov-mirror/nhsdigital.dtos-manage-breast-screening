from unittest.mock import MagicMock, patch

import pytest

from manage_breast_screening.notifications.management.commands.collect_metrics import (
    Command,
)
from manage_breast_screening.notifications.services.metrics import Metrics
from manage_breast_screening.notifications.services.queue import Queue


class TestCollectMetrics:
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        monkeypatch.setenv("ENVIRONMENT", "test")

    @patch.object(Queue, "get_message_count", side_effect=[8, 2])
    def test_handle_sends_queue_lengths(self, mock_message_count):
        mock_metrics_1 = MagicMock(spec=Metrics)
        mock_metrics_2 = MagicMock(spec=Metrics)

        with patch(
            f"{Command.__module__}.Metrics",
            side_effect=[mock_metrics_1, mock_metrics_2],
        ) as mock_metrics_class:
            Command().handle()

        mock_metrics_class.assert_any_call(
            "notifications-message-batch-retries", "messages", "Queue length", "test"
        )
        mock_metrics_class.assert_any_call(
            "notifications-message-status-updates", "messages", "Queue length", "test"
        )
        mock_metrics_1.add.assert_called_once_with("queue_name", 8)
        mock_metrics_2.add.assert_called_once_with("queue_name", 2)
