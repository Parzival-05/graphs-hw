import csv
from dataclasses import dataclass, field
import logging
import random
import time


from pyspla import Matrix

import bfs_parents
from experiment_utils import (
    EXPERIMENT_DATASET_PATH,
    get_files_in_directory,
    remove_outliers_ci,
)

BFSP_EXPERIMENT_DATASET_PATH = EXPERIMENT_DATASET_PATH / "bfsp"
RANDOM_SEED = 42
N = 5


@dataclass
class GraphStats:
    vertices: int
    edges: int


def parse_graph(path, delim=",", has_header=False):
    I = []  # noqa: E741
    J = []
    edges = 0
    nodes = 0
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=delim)
        if has_header:
            next(reader)
        for a in reader:
            v_from, v_to = a
            v_from, v_to = int(v_from), int(v_to)
            nodes = max(nodes, v_from)
            nodes = max(nodes, v_to)
            I.append(v_from)
            J.append(v_to)
            edges += 1
    V = [1] * edges
    return Matrix.from_lists(I, J, V, (edges, edges)), GraphStats(
        vertices=nodes, edges=edges
    )


def run_experiment(graph: Matrix, graph_stats: GraphStats, num_vertices):
    n = graph_stats.vertices
    random.seed(RANDOM_SEED)
    result = []
    for num_vertice in num_vertices:
        execution_times = []
        for _ in range(N):
            vertices = random.sample(range(n), num_vertice)
            start_time = time.perf_counter()
            bfs_parents.bfs_parents(vertices, graph)
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            execution_times.append(execution_time)
        execution_times = remove_outliers_ci(execution_times)
        mean_time = execution_times.mean()
        std_time = execution_times.std()
        result.append((num_vertice, mean_time, std_time))
    return result


@dataclass
class GraphParsingInfo:
    name: str
    delim: str = field(default=",")
    has_header: bool = field(default=True)


def main():
    if BFSP_EXPERIMENT_DATASET_PATH.is_dir():
        dir_files = get_files_in_directory(BFSP_EXPERIMENT_DATASET_PATH)
    else:
        logging.error("Директория c датасетом не найдена")
        return 1

    num_vertices = [3, 30]

    print(f"{RANDOM_SEED = }")
    print(f"{num_vertices = }")
    headers = [
        "Имя графа",
        "Стартовые вершины",
        "Вершины",
        "Рёбра",
        "Среднее время на вершину (с)",
        "Среднее время (с)",
        "С.О.",
    ]
    print("", *headers, sep="|", end="|")
    print()
    print("", *(["-"] * len(headers)), sep="|", end="|")
    print()
    graphs = {
        "musae_facebook_edges": GraphParsingInfo(
            name="musae_facebook_edges", delim=",", has_header=True
        ),
        "facebook_combined": GraphParsingInfo(
            name="facebook_combined", delim=" ", has_header=False
        ),
    }
    for path, name in dir_files:
        if name in graphs:
            delim = graphs[name].delim
            has_header = graphs[name].has_header
        else:
            delim = GraphParsingInfo.delim
            has_header = GraphParsingInfo.has_header

        G, graph_stats = parse_graph(path, delim, has_header)
        result = run_experiment(G, graph_stats, num_vertices=num_vertices)
        for num_vertice, mean_time, std_time in result:
            print(
                f"| {name} | {num_vertice} | {graph_stats.vertices} | {graph_stats.edges} | {(mean_time / num_vertice):.2f} | {mean_time:.2f} | {std_time:.2f} |"
            )


if __name__ == "__main__":
    main()
