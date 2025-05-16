import argparse
from enum import StrEnum
import logging
import random
import time


from pydantic import Field
from pydantic_core import ArgsKwargs
from pyspla import Matrix

import bfs_parents.bfs_parents as bfs_parents
from bfs_parents.experiment_details import (
    bfsp_reachable_count_dataset_path,
    parse_reachable_node_count,
)
from common.dataset_utils import DatasetConfig, Parseable, parse_graph
from common.experiment_utils import (
    get_files_in_directory,
    remove_outliers_ci,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filemode="a",
    filename="experiment.log",
)


class SelectNodeStrategy(StrEnum):
    TOP = "top"  # top means selection nodes with the highest reachable count
    BOTTOM = "bottom"  # bottom means selection nodes with the lowest reachable count

    def __repr__(self):
        return self.value


class BFSPExperimentConfig(Parseable):
    dataset_config: DatasetConfig
    count_vertices: list[int]
    random_seed: int
    n_repeats: int = Field(ge=1)
    selection_strategies: list[SelectNodeStrategy]
    selected_graphs: list[str] | None

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
            "help": "Количество повторов эксперимента",
            "default": 5,
        }
        n_repeats_parse_config = ArgsKwargs(n_repeats_args, n_repeats_kwargs)

        selection_strategies_args = ("--selection_strategies",)
        selection_strategies_kwargs = {
            "type": SelectNodeStrategy,
            "nargs": "+",
            "help": "Выбор вершин (top или bottom)",
            "default": [SelectNodeStrategy.BOTTOM, SelectNodeStrategy.TOP],
        }
        selection_strategies_parse_config = ArgsKwargs(
            selection_strategies_args, selection_strategies_kwargs
        )

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

        return [
            count_vertices_parse_config,
            random_seed_parse_config,
            n_repeats_parse_config,
            selection_strategies_parse_config,
            selected_graphs_parse_config,
            *DatasetConfig.get_parse_info(),
        ]


def run_experiment(
    graph: Matrix,
    bfsp_experiment_config: BFSPExperimentConfig,
    reachable_node_count: list[tuple[int, int]],
    selection_strategy: SelectNodeStrategy,
):
    random.seed(bfsp_experiment_config.random_seed)
    for num_vertice in bfsp_experiment_config.count_vertices:
        execution_times = []
        if selection_strategy == SelectNodeStrategy.TOP:
            vertices = reachable_node_count[:num_vertice]
        else:
            vertices = reachable_node_count[-num_vertice:]
        logging.debug(f"Selection strategy: {selection_strategy}. Vertices: {vertices}")
        vertices = list(map(lambda x: x[0], vertices))
        for _ in range(bfsp_experiment_config.n_repeats):
            start_time = time.perf_counter()
            bfs_parents.bfs_parents(vertices, graph)
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            execution_times.append(execution_time)
        execution_times = remove_outliers_ci(execution_times)
        mean_time = execution_times.mean()
        std_time = execution_times.std()
        yield ((num_vertice, mean_time, std_time))


def main(bfsp_experiment_config: BFSPExperimentConfig):
    dataset_path = bfsp_experiment_config.dataset_config.dataset_path
    dir_files = get_files_in_directory(dataset_path)

    random_seed = bfsp_experiment_config.random_seed
    count_vertices = bfsp_experiment_config.count_vertices
    n_repeats = bfsp_experiment_config.n_repeats
    selection_strategies = bfsp_experiment_config.selection_strategies
    selected_graphs = bfsp_experiment_config.selected_graphs

    print(f"{random_seed = }")
    print(f"{count_vertices = }")
    print(f"{n_repeats = }")
    print(f"{selection_strategies = }")
    if selected_graphs:
        print(f"{selected_graphs = }")
    else:
        print("selected_graphs = all graphs")
    headers = [
        "Имя графа",
        "Стартовые вершины",
        "Вершины",
        "Рёбра",
        "Среднее время на вершину (с)",
        "Среднее время (с)",
        "С.О.",
        "Стратегия выбора вершин",
    ]
    print("", *headers, sep="|", end="|\n")
    print("", *(["-"] * len(headers)), sep="|", end="|\n")
    for path, name in dir_files:
        logging.debug(f"Starting experiment for {name}...")
        if selected_graphs is not None and name not in selected_graphs:
            logging.debug(f"Skipping {name} as it is not selected")
            continue
        logging.debug(f"Try to parse graph {name} in {path}")
        G, graph_stats = parse_graph(path)
        reachable_node_count_path = (
            bfsp_reachable_count_dataset_path(path.parent) / f"{name}.csv"
        )
        logging.debug(
            f"Try to parse reachable node count {name} in {reachable_node_count_path}"
        )
        try:
            reachable_node_count = parse_reachable_node_count(reachable_node_count_path)
        except FileNotFoundError:
            logging.error(
                f"File {reachable_node_count_path} with reachable node count not found"
            )
            raise RuntimeError(
                f"Файл {reachable_node_count_path} с количеством достижимых вершин не найден. Используйте bfsp_feature_extractor.py для излвечения данных."
            )
        reachable_node_count.sort(key=lambda x: x[1], reverse=True)
        for select_strategy in selection_strategies:
            result = run_experiment(
                G,
                bfsp_experiment_config=bfsp_experiment_config,
                reachable_node_count=reachable_node_count,
                selection_strategy=select_strategy,
            )
            for num_vertice, mean_time, std_time in result:
                print(
                    f"| {name} | {num_vertice} | {graph_stats.vertices} | {graph_stats.edges} | {(mean_time / num_vertice):.2f} | {mean_time:.2f} | {std_time:.2f} | {select_strategy} |"
                )
        logging.debug(f"Finished experiment for {name}")


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
