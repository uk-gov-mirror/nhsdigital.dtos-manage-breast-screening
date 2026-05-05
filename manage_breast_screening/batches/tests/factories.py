from factory.declarations import Sequence
from factory.django import DjangoModelFactory
from factory.faker import Faker

from manage_breast_screening.batches.models import Batch


class BatchFactory(DjangoModelFactory):
    class Meta:
        model = Batch

    bso_batch_id = Sequence(lambda n: f"BATCH-{n:05d}")
    title = Faker("words", nb=3)
