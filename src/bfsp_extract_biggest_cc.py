import argparse
import os

import networkx
from pydantic_core import ArgsKwargs


from common.dataset_utils import DatasetConfig, Parseable, parse_graph_networkx
from common.experiment_utils import (
    bfsp_extracted_biggest_cc_path,
    get_files_in_directory,
)


class ExtractBiggectCCConfig(Parseable):
    dataset_config: DatasetConfig
    selected_graphs: list[str] | None

    @classmethod
    def get_parse_info(cls) -> list[ArgsKwargs]:
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
            selected_graphs_parse_config,
            *DatasetConfig.get_parse_info(),
        ]


def main(extract_biggest_cc_config: ExtractBiggectCCConfig):
    dir_files = get_files_in_directory(
        extract_biggest_cc_config.dataset_config.dataset_path
    )
    for path, name in dir_files:
        if name not in extract_biggest_cc_config.selected_graphs:
            continue
        print("Обработка %s..." % name)
        G = parse_graph_networkx(path)
        G_undirected = G.to_undirected()
        biggest_cc = max(networkx.connected_components(G_undirected), key=len)
        added = set()
        reenumerated_nodes = {}
        for v_from in biggest_cc:
            for _, v_to in G.edges(v_from):
                if v_to not in biggest_cc:
                    continue
                if (v_from, v_to) not in added:
                    if v_to not in reenumerated_nodes:
                        reenumerated_nodes[v_to] = len(reenumerated_nodes)
                    if v_from not in reenumerated_nodes:
                        reenumerated_nodes[v_from] = len(reenumerated_nodes)
                    added.add((v_from, v_to))
        output_file_path = bfsp_extracted_biggest_cc_path(path.parent) / f"{name}.csv"
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        with open(output_file_path, "w", encoding="utf-8") as file:
            for v_from, v_to in added:
                file.write(f"{reenumerated_nodes[v_from]} {reenumerated_nodes[v_to]}\n")

        print("Количество вершин:", len(biggest_cc))
        print("Количество ребер:", len(added))

        print("Результат сохранен в", output_file_path)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Извлечение самой большой К.С. для графа"
    )
    argskwargs_list = ExtractBiggectCCConfig.get_parse_info()
    for argskwargs in argskwargs_list:
        if argskwargs.kwargs is None:
            parser.add_argument(*argskwargs.args)
        else:
            parser.add_argument(*argskwargs.args, **argskwargs.kwargs)
    args = parser.parse_args()
    bfsp_experiment_config = ExtractBiggectCCConfig.parse(args)
    main(bfsp_experiment_config)
