# BFS-parents c SPLA, SuiteSparse:GraphBLAS

## Cборка SPLA
```
cmake .
make
```

## Установка pyspla

Инициализируйте виртуальное окружение:
```
python -m virtualenv .venv
source .venv/bin/activate
```

Установите pyspla:
```
pip install _deps/spla-src/python
cp _deps/spla-build/libspla_x64.so .venv/lib/python{PYTHON_VERSION}/site-packages/pyspla/libspla_x64.so
```
N.B.: `PYTHON_VERSION` >= 3.11

Установите библиотеки:
```
pip install -r requirements.txt
```
## Запуск

BFS-parents


```
cd src
python experiment_bfs.py
```

## Пример вывода 

### BFS-parents
1. Извлечение самой крупной К.С. (если требуется)

```bash
root@Parzival:~$ python bfsp_extract_biggest_cc.py --dataset_path ../../experiment_graphs/bfsp/graphs/
Обработка facebook_combined...
Количество вершин:  4039
Количество ребер:  88234
Результат сохранен в ../../experiment_graphs/bfsp/biggest_cc/facebook_combined.csv
Обработка musae_facebook_edges...
Количество вершин:  22470
Количество ребер:  171002
Результат сохранен в ../../experiment_graphs/bfsp/biggest_cc/musae_facebook_edges.csv
```
---

2. Запуск эксперимента

```
root@Parzival:~$ python bfsp_experiment.py --dataset_path ./../experiment_graphs/bfsp/biggest_cc/ --count_vertices 3 30 100 --n_repeats 10 --n_trials 5 --random_seed 42 --algo spla --selected_graphs facebook_combined musae_facebook_edges
random_seed = 42
count_vertices = [3, 30, 100]
n_repeats = 10
n_trials = 5
algo = spla
```
| Имя графа            | Алгоритм | Стартовые вершины | Вершины | Рёбра  | Среднее время на вершину (с) | Среднее время (с) | С.О. |
| -------------------- | -------- | ----------------- | ------- | ------ | ---------------------------- | ----------------- | ---- |
| facebook_combined    | spla     | 3                 | 4039    | 88234  | 0.006                        | 0.02              | 0.00 |
| facebook_combined    | spla     | 30                | 4039    | 88234  | 0.006                        | 0.17              | 0.02 |
| facebook_combined    | spla     | 100               | 4039    | 88234  | 0.005                        | 0.54              | 0.07 |
| musae_facebook_edges | spla     | 3                 | 22470   | 171002 | 0.024                        | 0.07              | 0.01 |
| musae_facebook_edges | spla     | 30                | 22470   | 171002 | 0.023                        | 0.70              | 0.04 |
| musae_facebook_edges | spla     | 100               | 22470   | 171002 | 0.024                        | 2.37              | 0.06 |

```
root@Parzival:~$ python bfsp_experiment.py --dataset_path ./../experiment_graphs/bfsp/biggest_cc/ --count_vertices 3 30 100 --n_repeats 10 --n_trials 5 --random_seed 42 --algo graphblas --selected_graphs facebook_combined musae_facebook_edges
random_seed = 42
count_vertices = [3, 30, 100]
n_repeats = 10
n_trials = 5
algo = graphblas
selected_graphs = ['facebook_combined', 'musae_facebook_edges']
```
| Имя графа            | Алгоритм  | Стартовые вершины | Вершины | Рёбра  | Среднее время на вершину (с) | Среднее время (с) | С.О. |
| -------------------- | --------- | ----------------- | ------- | ------ | ---------------------------- | ----------------- | ---- |
| facebook_combined    | graphblas | 3                 | 4039    | 88234  | 0.004                        | 0.01              | 0.00 |
| facebook_combined    | graphblas | 30                | 4039    | 88234  | 0.003                        | 0.10              | 0.02 |
| facebook_combined    | graphblas | 100               | 4039    | 88234  | 0.004                        | 0.41              | 0.13 |
| musae_facebook_edges | graphblas | 3                 | 22470   | 171002 | 0.020                        | 0.06              | 0.02 |
| musae_facebook_edges | graphblas | 30                | 22470   | 171002 | 0.013                        | 0.40              | 0.04 |
| musae_facebook_edges | graphblas | 100               | 22470   | 171002 | 0.014                        | 1.41              | 0.08 |
