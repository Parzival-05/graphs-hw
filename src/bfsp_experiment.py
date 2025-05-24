import argparse
import logging
import random
import time
import tracemalloc
from typing import Any, Callable


import numpy as np
from pydantic import Field
from pydantic_core import ArgsKwargs

from common.algo_type import Algo
from common.dataset_utils import DatasetConfig, GraphStats, Parseable, parse_graph
from common.experiment_utils import (
    get_files_in_directory,
    remove_outliers_iqr,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="a",
    filename="experiment.log",
)

RANDINT_UPPER_BOUND = 10000


def get_algo(algo: Algo) -> Callable[[list[int], Any], Any]:
    if algo == Algo.SPLA:
        from bfs_parents_spla.bfs_parents import bfs_parents
    else:
        from bfs_parents_gb.bfs_parents import bfs_parents
    return bfs_parents


class BFSPExperimentConfig(Parseable):
    dataset_config: DatasetConfig
    count_vertices: list[int]
    random_seed: int
    n_repeats: int = Field(ge=1)
    n_trials: int = Field(ge=1)
    algo: Algo
    selected_graphs: list[str] | None
    memory: bool

    @classmethod
    def get_parse_info(cls) -> list[ArgsKwargs]:
        count_vertices_args = ("--count_vertices",)
        count_vertices_kwargs = {
            "type": int,
            "nargs": "+",
            "help": "Список с количеством стартовых вершин",
            "default": [3, 30],
        }
        count_vertices_parse_config = ArgsKwargs(
            count_vertices_args, count_vertices_kwargs
        )

        random_seed_args = ("--random_seed",)
        random_seed_kwargs = {
            "type": int,
            "help": "Случайный сид",
            "default": 42,
        }
        random_seed_parse_config = ArgsKwargs(random_seed_args, random_seed_kwargs)

        n_repeats_args = ("--n_repeats",)
        n_repeats_kwargs = {
            "type": int,
            "help": "Количество повторов в рамках одного эксперимента",
            "default": 5,
        }
        n_repeats_parse_config = ArgsKwargs(n_repeats_args, n_repeats_kwargs)

        n_trials_args = ("--n_trials",)
        n_trials_kwargs = {
            "type": int,
            "help": "Количество повторов эксперимента",
            "default": 5,
        }
        n_trials_parse_config = ArgsKwargs(n_trials_args, n_trials_kwargs)

        algo_args = ("--algo",)
        algo_kwargs = {
            "type": Algo,
            "help": "Алгоритм (spla, graphblas)",
        }
        algo_parse_config = ArgsKwargs(algo_args, algo_kwargs)

        selected_graphs_args = ("--selected_graphs",)
        selected_graphs_kwargs = {
            "type": str,
            "nargs": "+",
            "help": "Выбор графов из датасета (по умолчанию выбираются все графы из директории)",
            "default": None,
        }
        selected_graphs_parse_config = ArgsKwargs(
            selected_graphs_args, selected_graphs_kwargs
        )

        memory_args = ("--memory",)
        memory_kwargs = {
            "action": "store_true",
            "help": "Измерять потребление памяти вместо производительности",
        }
        memory_parse_config = ArgsKwargs(memory_args, memory_kwargs)
        return [
            count_vertices_parse_config,
            random_seed_parse_config,
            n_repeats_parse_config,
            n_trials_parse_config,
            algo_parse_config,
            selected_graphs_parse_config,
            memory_parse_config,
            *DatasetConfig.get_parse_info(),
        ]


def run_experiment(
    graph,
    graph_stats: GraphStats,
    bfsp_experiment_config: BFSPExperimentConfig,
    bfs_parents: Callable[[list[int], Any], Any],
):
    random.seed(bfsp_experiment_config.random_seed)
    all_vertices = list(range(graph_stats.vertices))
    n_trials = bfsp_experiment_config.n_trials
    for count_vertice in bfsp_experiment_config.count_vertices:
        seed = random.randint(0, RANDINT_UPPER_BOUND)
        random.seed(seed)
        measurements_all = np.zeros((n_trials), dtype=np.float32)
        for i in range(n_trials):
            measurements = []
            vertices = random.sample(all_vertices, k=count_vertice)
            for _ in range(bfsp_experiment_config.n_repeats):
                if bfsp_experiment_config.memory:
                    tracemalloc.start()
                    bfs_parents(vertices, graph)
                    _, peak = tracemalloc.get_traced_memory()
                    tracemalloc.stop()
                    measurement = peak / (1024**2)
                else:
                    start_time = time.perf_counter()
                    bfs_parents(vertices, graph)
                    end_time = time.perf_counter()
                    measurement = end_time - start_time
                measurements.append(measurement)
            measurements = remove_outliers_iqr(measurements)
            measurements_all[i] = measurements.mean()
        yield ((count_vertice, measurements_all.mean(), measurements_all.std()))


def main(bfsp_experiment_config: BFSPExperimentConfig):
    dataset_path = bfsp_experiment_config.dataset_config.dataset_path
    dir_files = get_files_in_directory(dataset_path)

    random_seed = bfsp_experiment_config.random_seed
    count_vertices = bfsp_experiment_config.count_vertices
    n_repeats = bfsp_experiment_config.n_repeats
    selected_graphs = bfsp_experiment_config.selected_graphs
    algo = bfsp_experiment_config.algo
    n_trials = bfsp_experiment_config.n_trials

    print(f"{random_seed = }")
    print(f"{count_vertices = }")
    print(f"{n_repeats = }")
    print(f"{n_trials = }")
    print(f"{algo = }")
    print(
        f"Режим измерения {'потребления памяти' if bfsp_experiment_config.memory else 'производительности'}"
    )
    if selected_graphs:
        print(f"{selected_graphs = }")
    else:
        print("selected_graphs = all graphs")
    headers = ["Имя графа", "Алгоритм", "Стартовые вершины", "Вершины", "Рёбра"]
    performance_headers = [
        "Среднее время на вершину (с)",
        "Среднее время (с)",
    ]
    memory_headers = [
        "Пиковое потребление памяти на вершину (MB)",
        "Пиковое потребление памяти (MB)",
    ]
    std_headers = [
        "С.О.",
    ]
    all_headers = (
        headers
        + (memory_headers if bfsp_experiment_config.memory else performance_headers)
        + std_headers
    )
    print(
        "",
        *all_headers,
        sep="|",
        end="|\n",
    )
    print("", *(["-"] * len(all_headers)), sep="|", end="|\n")
    algo_name = algo
    algo = get_algo(algo)
    for path, name in dir_files:
        logging.info(f"Starting experiment for {name}...")
        if selected_graphs is not None and name not in selected_graphs:
            logging.info(f"Skipping {name} as it is not selected")
            continue
        logging.info(f"Try to parse graph {name} in {path}")
        G, graph_stats = parse_graph(path, algo_name)
        result = run_experiment(
            G,
            graph_stats=graph_stats,
            bfsp_experiment_config=bfsp_experiment_config,
            bfs_parents=algo,
        )
        for count_vertice, mean, std in result:
            print(
                f"| {name} | {algo_name} | {count_vertice} | {graph_stats.vertices} | {graph_stats.edges} | {(mean / count_vertice):.3f} | {mean:.2f} | {std:.2f} |"
            )
        logging.info(f"Finished experiment for {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Запуск эксперимента с bfsp на spla")
    argskwargs_list = BFSPExperimentConfig.get_parse_info()
    for argskwargs in argskwargs_list:
        if argskwargs.kwargs is None:
            parser.add_argument(*argskwargs.args)
        else:
            parser.add_argument(*argskwargs.args, **argskwargs.kwargs)
    args = parser.parse_args()
    bfsp_experiment_config = BFSPExperimentConfig.parse(args)
    main(bfsp_experiment_config)
