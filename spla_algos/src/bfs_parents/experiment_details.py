import csv
from pathlib import Path


from common.experiment_utils import (
    EXPERIMENT_DATASET_PATH,
)


BFSP_EXPERIMENT_DATASET_PATH = EXPERIMENT_DATASET_PATH / "bfsp"
BFSP_FEATURE_EXTRACTOR_DELIM = ","
BFSP_FEATURE_EXTRACTOR_HAS_HEADER = True


def bfsp_reachable_count_dataset_path(dataset_path: Path):
    return dataset_path.parent / "bfsp_reachable_count"


def bfsp_extracted_biggest_cc_path(dataset_path: Path):
    return dataset_path.parent / "biggest_cc"


def parse_reachable_node_count(path: Path) -> list[tuple[int, int]]:
    res = []
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=BFSP_FEATURE_EXTRACTOR_DELIM)
        if BFSP_FEATURE_EXTRACTOR_HAS_HEADER:
            next(reader)
        for a in reader:
            v, count = a
            res.append((int(v), int(count)))
    return res
