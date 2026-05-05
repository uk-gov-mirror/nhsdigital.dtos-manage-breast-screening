from django.conf import settings
from django.db import transaction

from ...dicom.models import ReadingSession, ReadingSessionItem


class NoImagesToRead(Exception):
    pass


class ReadingSessionService:
    def __init__(self, reader, provider):
        self.reader = reader
        self.provider = provider

    @transaction.atomic
    def assign_item_to_new_session(self) -> ReadingSessionItem:
        queue = (
            self.provider.image_reading_cases.unassigned()
            .where_same_study_has_not_been_assigned_to_reader(self.reader)
            .order_by("created_at", "id")
            .select_for_update(skip_locked=True)
        )

        case = queue.first()
        if case is None:
            raise NoImagesToRead

        session = ReadingSession.objects.create(
            reader=self.reader, session_size=settings.READING_SESSION_DEFAULT_SIZE
        )
        item = session.items.create(session=session, case=case, reading_order=1)

        return item
