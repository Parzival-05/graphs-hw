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

RANDOM_SEED = 42
num_vertices = [3, 30]
| Имя графа            | Стартовые вершины | Вершины | Рёбра  | Среднее время на вершину (с) | Среднее время (с) | С.О. |
| -------------------- | ----------------- | ------- | ------ | ---------------------------- | ----------------- | ---- |
| facebook_combined    | 3                 | 4038    | 88234  | 0.11                         | 0.34              | 0.00 |
| facebook_combined    | 30                | 4038    | 88234  | 0.08                         | 2.40              | 0.02 |
| musae_facebook_edges | 3                 | 22469   | 171002 | 0.26                         | 0.78              | 0.10 |
| musae_facebook_edges | 30                | 22469   | 171002 | 0.16                         | 4.80              | 0.07 |