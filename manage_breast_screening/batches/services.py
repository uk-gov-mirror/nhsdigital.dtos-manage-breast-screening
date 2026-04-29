import logging

import pandas as pd
from django.db import transaction

from manage_breast_screening.batches.models import Batch

logger = logging.getLogger(__name__)


def create_batch_from_csv(csv) -> Batch:
    """
    Convert a BSS batch csv to a Batch object.
    """

    bso_batch_id, title = parse_batch_csv(csv)

    logger.info(f"creating batch with title {title}")
    try:
        with transaction.atomic():
            batch = Batch(bso_batch_id=bso_batch_id, title=title)
            batch.save()
    except Exception as e:
        logger.error(f"Error saving batch: {e}")
        raise
    else:
        return batch


def parse_batch_csv(csv):
    df = pd.read_csv(csv, header=None, names=range(11))

    parameters_idx = (df[0] == "Batch Parameters").idxmax()
    bso_batch_id = df.iloc[parameters_idx + 1, 1]
    title = df.iloc[parameters_idx + 2, 1]

    return bso_batch_id, title
