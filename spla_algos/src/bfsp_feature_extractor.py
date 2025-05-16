import argparse
import csv
import math
import os

from pydantic_core import ArgsKwargs
from tqdm import tqdm


from bfs_parents.experiment_details import (
    bfsp_reachable_count_dataset_path,
)
from bfs_parents.extract_reachable_count import extract_reachable_count
from common.dataset_utils import DatasetConfig, Parseable, parse_graph
from common.experiment_utils import (
    get_files_in_directory,
)


class BFSPFeatureExtractConfig(Parseable):
    dataset_config: DatasetConfig
    chunk_size: int
    selected_graphs: list[str] | None

    @classmethod
    def get_parse_info(cls) -> list[ArgsKwargs]:
        chunk_size_args = ("--chunk_size",)
        chunk_size_kwargs = {
            "type": int,
            "help": "Chunk size",
            "default": 10,
        }
        chunk_size_parse_config = ArgsKwargs(chunk_size_args, chunk_size_kwargs)

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
            chunk_size_parse_config,
            selected_graphs_parse_config,
            *DatasetConfig.get_parse_info(),
        ]


def main(bfsp_feature_extract_config: BFSPFeatureExtractConfig):
    dir_files = get_files_in_directory(
        bfsp_feature_extract_config.dataset_config.dataset_path
    )
    chunk_size = bfsp_feature_extract_config.chunk_size
    print(f"{chunk_size = }")
    for path, name in dir_files:
        res: dict[int, int] = {}
        if name not in bfsp_feature_extract_config.selected_graphs:
            continue
        print("Обработка %s..." % name)
        try:
            G, graph_stats = parse_graph(path)
            result_generator = extract_reachable_count(
                G, nodes=list(range(graph_stats.vertices)), chunk_size=chunk_size
            )
            for result_batch in tqdm(
                result_generator, total=math.ceil(graph_stats.vertices / chunk_size)
            ):
                res.update(result_batch)
        finally:
            output_file_path = bfsp_reachable_count_dataset_path(path.parent) / f"{name}.csv"
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            with open(output_file_path, "w", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["node", "reachable_count"])
                for node, reachable_count in res.items():
                    writer.writerow([node, reachable_count])
            print(f"{name = } обработан")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Извлечение признаков для bfs_parents")
    argskwargs_list = BFSPFeatureExtractConfig.get_parse_info()
    for argskwargs in argskwargs_list:
        if argskwargs.kwargs is None:
            parser.add_argument(*argskwargs.args)
        else:
            parser.add_argument(*argskwargs.args, **argskwargs.kwargs)
    args = parser.parse_args()
    bfsp_experiment_config = BFSPFeatureExtractConfig.parse(args)
    main(bfsp_experiment_config)
