import logging
import os
from pathlib import Path

import numpy as np
from scipy import stats


EXPERIMENT_DATASET_PATH = Path("../experiment_graphs").resolve(strict=True)

BFSP_EXPERIMENT_DATASET_PATH = EXPERIMENT_DATASET_PATH / "bfsp"
BFSP_FEATURE_EXTRACTOR_DELIM = ","
BFSP_FEATURE_EXTRACTOR_HAS_HEADER = True


def bfsp_extracted_biggest_cc_path(dataset_path: Path):
    return dataset_path.parent / "biggest_cc"


def get_files_in_directory(directory):
    try:
        files = os.listdir(directory)
        file_paths = [
            (Path(os.path.join(directory, file)), file.split(".")[0])
            for file in files
            if os.path.isfile(os.path.join(directory, file))
        ]
        return file_paths
    except FileNotFoundError:
        logging.error(f"Директория '{directory}' не найдена.")
        return []


def remove_outliers_iqr(data: list[float], iqr_coef=1.5) -> np.ndarray:
    data = np.array(data)  # type: ignore
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower = q1 - iqr_coef * iqr
    upper = q3 + iqr_coef * iqr
    return data[(data >= lower) & (data <= upper)]  # type: ignore
