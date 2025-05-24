import random
from typing import Tuple

import pytest
from bfs_parents_gb.bfs_parents import bfs_parents as bfs_parents_gb
from bfs_parents_spla.bfs_parents import bfs_parents as bfs_parents_spla
from common.algo_type import Algo
from common.dataset_utils import parse_graph
from common.experiment_utils import BFSP_EXPERIMENT_DATASET_PATH
from common.gb_to_spla import extract_ijv_from_gb

test_cases = [
    (BFSP_EXPERIMENT_DATASET_PATH / "graphs" / "facebook_combined.csv", 100),
]


def compare_algos(G_spla, G_gb, nodes: list[int]):
    answer_spla = bfs_parents_spla(nodes, G_spla)
    answer_gb = bfs_parents_gb(nodes, G_gb)
    ijv_spla: Tuple[list, list, list] = answer_spla.to_lists()
    ijv_gb: Tuple[list, list, list] = extract_ijv_from_gb(answer_gb)
    assert ijv_spla == ijv_gb


@pytest.mark.parametrize("G_path, node_count", test_cases)
def test_compared(G_path, node_count: int):  # type: ignore
    G_spla, _ = parse_graph(G_path, Algo.SPLA)
    G_gb, graph_stats = parse_graph(G_path, Algo.GRAPHBLAS)
    node_count: int = min(node_count, graph_stats.vertices)
    compare_algos(
        G_spla, G_gb, nodes=random.sample(range(graph_stats.vertices), k=node_count)
    )
