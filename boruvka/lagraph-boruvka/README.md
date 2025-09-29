# LAGraph Boruvka MSF Benchmark

Implementation of Boruvka's algorithm for Minimum Spanning Forest using LAGraph in standalone mode.

## Requirements

- GCC with C11 support and OpenMP
- LAGraph library
- GraphBLAS library
- SuiteSparse (recommended)

## Getting Started

### Install Dependencies (Ubuntu/Debian)

```bash
sudo apt-get install build-essential libsuitesparse-dev liblapack-dev libblas-dev

# Install GraphBLAS from source
git clone https://github.com/DrTimothyAldenDavis/GraphBLAS.git
cd GraphBLAS && make library && sudo make install

# Install LAGraph from source
git clone https://github.com/GraphBLAS/LAGraph.git
cd LAGraph && make library && sudo make install
sudo ldconfig
```

### Build

```bash
make all
make test
```

### Run

```bash
./boruvka_bench input_graph.mtx

# Verbose output
./boruvka_bench -v input_graph.mtx

# Machine-readable CSV output
./boruvka_bench -t input_graph.mtx

# Quiet mode
./boruvka_bench -q input_graph.mtx
```

## Input Format

Input files should be in Matrix Market format (.mtx):
```
%%MatrixMarket matrix coordinate integer symmetric
4 4 6
1 2 5
1 3 2
2 3 3
2 4 1
3 4 4
4 1 6
```

This represents an undirected graph where:
- Line 1: Header (Matrix Market format)
- Line 2: rows cols entries (4 nodes, 4 nodes, 6 edges)
- Remaining lines: source destination weight (1-indexed)

## Output Format

### Human-readable mode:
```
Nodes: 4, Edges: 6
MSF edges: 3, MSF weight: 8.00
Components: 1
Execution time: 0.000123 seconds
```

### Machine-readable CSV mode (-t):
```
execution_time,nodes,edges,msf_edges,msf_weight,components
0.000123,4,6,3,8.00,1
```

## Testing

```bash
make test

# Performance benchmarks
cd tests && ./run_performance.sh
```

The test suite validates algorithm correctness on various graph types (triangle, path, complete graph, disconnected components).

