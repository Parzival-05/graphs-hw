#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <getopt.h>
#include <math.h>
#include "LAGraphX.h"

// Function to compare doubles for qsort
int compare_doubles(const void *a, const void *b) {
    double da = *(const double*)a;
    double db = *(const double*)b;
    return (da > db) - (da < db);
}

// Calculate statistics from timing array
typedef struct {
    double mean;
    double median;
    double std_dev;
    double min;
    double max;
} timing_stats;

void calculate_stats(double *times, int n, timing_stats *stats) {
    // Sort array for median calculation
    double *sorted_times = malloc(n * sizeof(double));
    memcpy(sorted_times, times, n * sizeof(double));
    qsort(sorted_times, n, sizeof(double), compare_doubles);
    
    // Calculate min and max
    stats->min = sorted_times[0];
    stats->max = sorted_times[n-1];
    
    // Calculate mean
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
        sum += times[i];
    }
    stats->mean = sum / n;
    
    // Calculate median
    if (n % 2 == 0) {
        stats->median = (sorted_times[n/2 - 1] + sorted_times[n/2]) / 2.0;
    } else {
        stats->median = sorted_times[n/2];
    }
    
    // Calculate standard deviation
    double variance = 0.0;
    for (int i = 0; i < n; i++) {
        variance += pow(times[i] - stats->mean, 2);
    }
    variance /= n;
    stats->std_dev = sqrt(variance);
    
    free(sorted_times);
}

double get_time_seconds() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

// Function to count unique components
int count_components(GrB_Vector componentId, int n) {
    if (componentId == NULL) return -1;
    
    bool *seen = calloc(n, sizeof(bool));
    if (!seen) return -1;
    
    int component_count = 0;
    for (int i = 0; i < n; i++) {
        uint64_t comp;
        GrB_Info info = GrB_Vector_extractElement_UINT64(&comp, componentId, i);
        if (info == GrB_SUCCESS && comp < n && !seen[comp]) {
            seen[comp] = true;
            component_count++;
        }
    }
    
    free(seen);
    return component_count;
}

void print_usage(const char* program_name) {
    printf("Usage: %s [OPTIONS] <input_file.mtx>\n", program_name);
    printf("Options:\n");
    printf("  -h, --help      Show this help message\n");
    printf("  -v, --verbose   Enable verbose output\n");
    printf("  -q, --quiet     Suppress non-essential output\n");
    printf("  -t, --time      Output timing information in machine-readable format\n");
    printf("  -n, --runs=N    Number of benchmark runs (default: 1)\n");
    printf("\nBenchmark LAGraph MSF (Boruvka's algorithm) on Matrix Market files.\n");
    printf("For single run: execution_time_ms,nodes,edges,msf_edges,msf_weight,components\n");
    printf("For multiple runs: mean_time_ms,median_time_ms,std_dev_ms,min_time_ms,max_time_ms,nodes,edges,msf_edges,msf_weight,components\n");
}

int main(int argc, char **argv) {
    bool verbose = false;
    bool quiet = false;
    bool machine_readable = false;
    int num_runs = 1;
    int warmup_runs = 10;
    
    // Parse command line options
    static struct option long_options[] = {
        {"help",    no_argument,       0, 'h'},
        {"verbose", no_argument,       0, 'v'},
        {"quiet",   no_argument,       0, 'q'},
        {"time",    no_argument,       0, 't'},
        {"runs",    required_argument, 0, 'n'},
        {0, 0, 0, 0}
    };
    
    int c;
    while ((c = getopt_long(argc, argv, "hvqtn:", long_options, NULL)) != -1) {
        switch (c) {
            case 'h':
                print_usage(argv[0]);
                return 0;
            case 'v':
                verbose = true;
                break;
            case 'q':
                quiet = true;
                break;
            case 't':
                machine_readable = true;
                break;
            case 'n':
                num_runs = atoi(optarg);
                if (num_runs <= 0) {
                    if (!quiet) fprintf(stderr, "Error: Number of runs must be positive\n");
                    return 1;
                }
                break;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }
    
    if (optind >= argc) {
        if (!quiet) fprintf(stderr, "Error: No input file specified\n");
        print_usage(argv[0]);
        return 1;
    }
    
    const char* input_file = argv[optind];
    
    // Initialize LAGraph
    char msg[LAGRAPH_MSG_LEN];
    int info = LAGraph_Init(msg);
    if (info != GrB_SUCCESS) {
        if (!quiet) fprintf(stderr, "Failed to initialize LAGraph: %s\n", msg);
        return 1;
    }
    
    if (!quiet && !machine_readable) {
        printf("LAGraph MSF (Boruvka) Benchmark\n");
        printf("==============================\n");
        printf("Input file: %s\n", input_file);
        printf("Number of runs: %d\n", num_runs);
    }
    
    // Load the graph
    GrB_Matrix A = NULL;
    GrB_Matrix forest_edges = NULL;
    GrB_Vector componentId = NULL;
    
    FILE *f = fopen(input_file, "r");
    if (f == NULL) {
        if (!quiet) fprintf(stderr, "Cannot open file: %s\n", input_file);
        LAGraph_Finalize(msg);
        return 1;
    }
    
    info = LAGraph_MMRead(&A, f, msg);
    fclose(f);
    
    if (info != GrB_SUCCESS) {
        if (!quiet) fprintf(stderr, "Failed to load Matrix Market file: %s\n", msg);
        LAGraph_Finalize(msg);
        return 1;
    }
    
    // Get graph properties
    GrB_Index nrows, ncols, nvals;
    GrB_Matrix_nrows(&nrows, A);
    GrB_Matrix_ncols(&ncols, A);
    GrB_Matrix_nvals(&nvals, A);
    
    if (verbose) {
        printf("Graph loaded: %lu nodes, %lu edges\n", nrows, nvals);
    }
    
    // Allocate array for timing results
    double *execution_times = malloc(num_runs * sizeof(double));
    if (!execution_times) {
        if (!quiet) fprintf(stderr, "Failed to allocate memory for timing results\n");
        GrB_Matrix_free(&A);
        LAGraph_Finalize(msg);
        return 1;
    }
    
    // Variables to store final results (from last run)
    GrB_Index msf_edges = 0;
    double total_weight = 0.0;
    int num_components = 0;
    
    // Run benchmark N times
    for (int run = 0; run < num_runs + warmup_runs; run++) {
        if (verbose && num_runs > 1) {
            printf("Run %d/%d...\n", run + 1 - warmup_runs, num_runs);
        }
        
        // Clean up previous results if not first run
        if (run > 0) {
            GrB_Matrix_free(&forest_edges);
            GrB_Vector_free(&componentId);
            forest_edges = NULL;
            componentId = NULL;
        }

        // Warmup runs do not collect timing data
        if (run < warmup_runs) {
            // Skip timing for warmup runs
            info = LAGraph_msf(&forest_edges, &componentId, A, true, msg);
            continue;
        }

        // Benchmark the MSF algorithm
        double start_time = get_time_seconds();
        info = LAGraph_msf(&forest_edges, &componentId, A, true, msg);
        double end_time = get_time_seconds();
        // printf("Run %d: %.3f ms\n", run + 1, (end_time - start_time) * 1000.0);
        execution_times[run-warmup_runs] = (end_time - start_time) * 1000.0; // Convert to milliseconds
        
        if (info != GrB_SUCCESS) {
            if (!quiet) fprintf(stderr, "LAGraph_msf failed on run %d: %s\n", run + 1, msg);
            free(execution_times);
            GrB_Matrix_free(&A);
            LAGraph_Finalize(msg);
            return 1;
        }
        
        // Get MSF results (store from last successful run)
        GrB_Matrix_nvals(&msf_edges, forest_edges);
        
        total_weight = 0.0;
        GrB_Matrix_reduce_FP64(&total_weight, GrB_NULL, 
                              GrB_PLUS_MONOID_FP64, forest_edges, GrB_NULL);
        
        num_components = count_components(componentId, (int)nrows);
    }
    
    // Calculate timing statistics
    timing_stats stats;
    calculate_stats(execution_times, num_runs, &stats);
    
    // Output results
    if (machine_readable) {
        if (num_runs == 1) {
            // Single run: time_ms,nodes,edges,msf_edges,msf_weight,components
            printf("%.3f,%lu,%lu,%lu,%.2f,%d\n", 
                   execution_times[0], nrows, nvals, msf_edges, total_weight, num_components);
        } else {
            // Multiple runs: mean_time_ms,median_time_ms,std_dev_ms,min_time_ms,max_time_ms,nodes,edges,msf_edges,msf_weight,components
            printf("%.3f,%.3f,%.3f,%.3f,%.3f,%lu,%lu,%lu,%.2f,%d\n", 
                   stats.mean, stats.median, stats.std_dev, stats.min, stats.max,
                   nrows, nvals, msf_edges, total_weight, num_components);
        }
    } else if (!quiet) {
        printf("\nResults:\n");
        if (num_runs == 1) {
            printf("Execution time: %.3f milliseconds\n", execution_times[0]);
        } else {
            printf("Timing Statistics (%d runs):\n", num_runs);
            printf("  Mean: %.3f milliseconds\n", stats.mean);
            printf("  Median: %.3f milliseconds\n", stats.median);
            printf("  Std Dev: %.3f milliseconds\n", stats.std_dev);
            printf("  Min: %.3f milliseconds\n", stats.min);
            printf("  Max: %.3f milliseconds\n", stats.max);
        }
        printf("MSF edges: %lu\n", msf_edges);
        printf("MSF total weight: %.2f\n", total_weight);
        printf("Number of components: %d\n", num_components);
    }
    
    // Cleanup
    free(execution_times);
    GrB_Matrix_free(&forest_edges);
    GrB_Vector_free(&componentId);
    GrB_Matrix_free(&A);
    LAGraph_Finalize(msg);
    
    return 0;
}