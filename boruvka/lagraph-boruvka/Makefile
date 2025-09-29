CC = gcc
CFLAGS = -O3 -std=c11 -fopenmp -DNDEBUG
INCLUDES = -I/usr/local/include/suitesparse -I$(HOME)/LAGraph/include -I$(HOME)/GraphBLAS/Include
LIBS = -L/usr/local/lib -llagraph -llagraphx -lgraphblas -lm -fopenmp 

# Try to use pkg-config if available
ifeq ($(shell pkg-config --exists lagraph && echo yes),yes)
    INCLUDES = $(shell pkg-config --cflags lagraph)
    LIBS = $(shell pkg-config --libs lagraph)
endif

TARGETS = boruvka_bench graph_converter
TEST_TARGETS = tests/msf_test
SOURCES = src/boruvka_bench.c src/graph_converter.c

all: $(TARGETS)

boruvka_bench: src/boruvka_bench.c
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $< $(LIBS)

graph_converter: src/graph_converter.c
	$(CC) $(CFLAGS) -o $@ $< -lm

tests/msf_test: tests/msf_test.c
	$(CC) $(CFLAGS) $(INCLUDES) -o $@ $< $(LIBS)

clean:
	rm -f $(TARGETS) $(TEST_TARGETS) *.mtx
	rm -rf tests/results

# Test targets
test: tests/msf_test
	cd tests && ./msf_test

test-framework: tests/msf_test
	@echo "Test framework built successfully"

test-clean: 
	rm -rf tests/results
	rm -f tests/msf_test

benchmark: boruvka_bench
	@echo "Pure benchmark (no tests, machine readable output):"
	@echo "Usage: ./boruvka_bench [-v] [-q] [-t] <input.mtx>"

# Run clean benchmark on a specific file
run-benchmark: boruvka_bench
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make run-benchmark FILE=<input.mtx>"; \
		echo "Example: make run-benchmark FILE=data/karate.mtx"; \
	else \
		./boruvka_bench -v $(FILE); \
	fi

.PHONY: all clean run-boruvka run-msf test test-framework test-clean convert-sample help benchmark run-benchmark