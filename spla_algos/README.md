# SPLA алгоритмы (BFS-parents, Борувка)

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
2. Извлечение количества достижимых вершин 
```console
root@Parzival:~$ python bfsp_feature_extractor.py --dataset_path ../../experiment_graphs/bfsp/biggest_cc/ --chunk_size 30  --selected_graphs facebook_combined musae_facebook_edges
chunk_size = 30
Обработка facebook_combined...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 135/135 [02:33<00:00,  1.14s/it]
name = 'facebook_combined' обработан

Обработка musae_facebook_edges...
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 749/749 [32:28<00:00,  2.60s/it]
name = 'musae_facebook_edges' обработан
```
---

3. Запуск эксперимента

```
root@Parzival:~$ python bfsp_experiment.py --dataset_path ../../experiment_graphs/bfsp/biggest_cc/ --count_vertices 3 30 100 --n_repeats 5
random_seed = 42
count_vertices = [3, 30, 100]
n_repeats = 5
selection_strategies = [bottom, top]
selected_graphs = all graphs
```

| Имя графа            | Стартовые вершины | Вершины | Рёбра  | Среднее время на вершину (с) | Среднее время (с) | С.О. | Стратегия выбора вершин |
| -------------------- | ----------------- | ------- | ------ | ---------------------------- | ----------------- | ---- | ----------------------- |
| facebook_combined    | 3                 | 4039    | 88234  | 0.08                         | 0.25              | 0.00 | bottom                  |
| facebook_combined    | 30                | 4039    | 88234  | 0.07                         | 2.17              | 0.03 | bottom                  |
| facebook_combined    | 100               | 4039    | 88234  | 0.08                         | 7.75              | 0.04 | bottom                  |
| facebook_combined    | 3                 | 4039    | 88234  | 0.09                         | 0.26              | 0.02 | top                     |
| facebook_combined    | 30                | 4039    | 88234  | 0.08                         | 2.40              | 0.08 | top                     |
| facebook_combined    | 100               | 4039    | 88234  | 0.09                         | 8.97              | 0.27 | top                     |
| musae_facebook_edges | 3                 | 22470   | 171002 | 0.14                         | 0.43              | 0.02 | bottom                  |
| musae_facebook_edges | 30                | 22470   | 171002 | 0.15                         | 4.52              | 0.11 | bottom                  |
| musae_facebook_edges | 100               | 22470   | 171002 | 0.16                         | 16.18             | 0.24 | bottom                  |
| musae_facebook_edges | 3                 | 22470   | 171002 | 0.19                         | 0.58              | 0.03 | top                     |
| musae_facebook_edges | 30                | 22470   | 171002 | 0.17                         | 5.17              | 0.06 | top                     |
| musae_facebook_edges | 100               | 22470   | 171002 | 0.16                         | 16.31             | 0.40 | top                     |