from abc import abstractmethod
from argparse import Namespace
from collections import defaultdict
import csv
from dataclasses import dataclass
from pathlib import Path


import networkx
from pydantic import BaseModel, field_validator
from pydantic_core import ArgsKwargs
from pyspla import Matrix

from bfs_parents.experiment_details import BFSP_EXPERIMENT_DATASET_PATH


@dataclass
class GraphStats:
    vertices: int
    edges: int


class Parseable(BaseModel):
    @classmethod
    @abstractmethod
    def get_parse_info(cls) -> list[ArgsKwargs]:  # clean code OFF
        raise NotImplementedError

    @classmethod
    def parse(cls, namespace: Namespace):
        args = dict(namespace._get_kwargs())
        cls_input = dict()
        fields = cls.model_fields
        parseable_fields: dict = dict()
        for field_name, value in fields.items():
            if issubclass(value.annotation, Parseable):  # type: ignore
                for parseable_field in value.annotation.model_fields.keys():
                    parseable_fields[parseable_field] = (
                        value.annotation,
                        field_name,
                    )
        parseable_items = defaultdict(lambda: [])
        for key, (value, _) in parseable_fields.items():
            parseable_items[value].append(key)
        for arg, value in args.items():
            if arg in parseable_fields:
                parseable_class, field_name = parseable_fields[arg]
                parseable_value = parseable_class.parse(namespace)
                cls_input[field_name] = parseable_value
                for key in parseable_items[parseable_class]:
                    del parseable_fields[key]
                del parseable_items[parseable_class]
                continue
            field_name = fields.get(arg)
            if field_name is not None:
                cls_input[arg] = value
        return cls(**cls_input)


class DatasetConfig(Parseable):
    dataset_path: Path

    @field_validator("dataset_path")
    def validate_dataset_path(cls, dataset_path):
        path = Path(dataset_path).resolve(strict=True)
        if not path.is_dir():
            raise ValueError("Директория c датасетом не найдена")
        return path

    @classmethod
    def get_parse_info(cls) -> list[ArgsKwargs]:
        dataset_path_args = ("--dataset_path",)
        dataset_path_kwargs = {
            "type": str,
            "help": "Path to the dataset directory",
            "default": BFSP_EXPERIMENT_DATASET_PATH,
        }
        dataset_path_parse_config = ArgsKwargs(dataset_path_args, dataset_path_kwargs)
        return [dataset_path_parse_config]


def parse_graph(path):
    I = []  # noqa: E741
    J = []
    edges = 0
    nodes = 0

    def parse_row(a):
        nonlocal edges, nodes
        v_from, v_to = a
        v_from, v_to = int(v_from), int(v_to)
        nodes = max(nodes, v_from)
        nodes = max(nodes, v_to)
        I.append(v_from)
        J.append(v_to)
        edges += 1

    for delim in CSV_FORMAT_DELIMS:
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=delim)
            header_or_v = next(reader)
            if len(header_or_v) != 2:
                continue
            first, second = header_or_v
            if first.isnumeric() and second.isnumeric():
                parse_row(header_or_v)
            for a in reader:
                parse_row(a)
            break
    else:
        raise RuntimeError(f"Failed to parse graph from {path}")
    V = [1] * edges
    return Matrix.from_lists(I, J, V, (edges, edges)), GraphStats(
        vertices=nodes + 1, edges=edges
    )


CSV_FORMAT_DELIMS = [",", " "]


def parse_graph_networkx(path):
    G = networkx.MultiDiGraph()
    nodes = set()

    def parse_row(a):
        v_from, v_to = a
        v_from, v_to = int(v_from), int(v_to)
        if v_from not in nodes:
            nodes.add(v_from)
            G.add_node(v_from)
        if v_to not in nodes:
            nodes.add(v_to)
            G.add_node(v_to)
        G.add_edge(v_from, v_to)

    for delim in CSV_FORMAT_DELIMS:
        with open(path, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=delim)
            header_or_v = next(reader)
            if len(header_or_v) != 2:
                continue
            first, second = header_or_v
            if first.isnumeric() and second.isnumeric():
                parse_row(header_or_v)
            for a in reader:
                parse_row(a)
            break
    else:
        raise RuntimeError(f"Failed to parse graph from {path}")
    return G
