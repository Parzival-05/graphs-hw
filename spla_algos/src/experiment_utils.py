import logging
import os
from pathlib import Path

import numpy as np
from scipy import stats


EXPERIMENT_DATASET_PATH = Path("../../experiment_graphs").resolve(strict=True)


def get_files_in_directory(directory):
    try:
        files = os.listdir(directory)
        file_paths = [
            (os.path.join(directory, file), file.split(".")[0])
            for file in files
            if os.path.isfile(os.path.join(directory, file))
        ]
        return file_paths
    except FileNotFoundError:
        logging.error(f"Директория '{directory}' не найдена.")
        return []


def remove_outliers_ci(data, confidence=0.95):
    data = np.array(data)
    mean = np.mean(data)
    sem = stats.sem(data)
    interval = stats.t.interval(confidence, len(data) - 1, loc=mean, scale=sem)
    return data[(data >= interval[0]) & (data <= interval[1])]
