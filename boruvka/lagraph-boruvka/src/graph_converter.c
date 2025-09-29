#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_LINE_LENGTH 10000

typedef struct {
    int from;
    int to;
    int weight;
} Edge;

typedef struct {
    Edge *edges;
    int num_edges;
    int capacity;
    int max_node_id;
} Graph;

// Initialize graph structure
void init_graph(Graph *g) {
    g->edges = NULL;
    g->num_edges = 0;
    g->capacity = 0;
    g->max_node_id = 0;
}

// Add edge to graph
void add_edge(Graph *g, int from, int to, int weight) {
    // Resize if needed
    if (g->num_edges >= g->capacity) {
        g->capacity = g->capacity == 0 ? 1000 : g->capacity * 2;
        g->edges = realloc(g->edges, g->capacity * sizeof(Edge));
        if (!g->edges) {
            fprintf(stderr, "Memory allocation failed\n");
            exit(1);
        }
    }
    
    // Add edge
    g->edges[g->num_edges].from = from;
    g->edges[g->num_edges].to = to;
    g->edges[g->num_edges].weight = weight;
    g->num_edges++;
    
    // Update max node ID
    if (from > g->max_node_id) g->max_node_id = from;
    if (to > g->max_node_id) g->max_node_id = to;
}

// Parse a line in the format: vertex_id neighbor1_id weight1 neighbor2_id weight2 ...
int parse_line(char *line, Graph *g) {
    char *token;
    int vertex_id;
    int neighbor_id;
    double weight;
    int state = 0; // 0=expecting vertex_id, 1=expecting neighbor_id, 2=expecting weight
    int edges_added = 0;
    
    // Remove newline if present
    char *newline = strchr(line, '\n');
    if (newline) *newline = '\0';
    
    // Skip empty lines and comments
    if (line[0] == '\0' || line[0] == '#' || line[0] == '%') {
        return 0;
    }
    
    token = strtok(line, " \t");
    
    while (token != NULL) {
        if (state == 0) {
            // Parse vertex ID
            vertex_id = atoi(token);
            state = 1;
        } else if (state == 1) {
            // Parse neighbor ID
            neighbor_id = atoi(token);
            state = 2;
        } else if (state == 2) {
            // Parse weight
            weight = atoi(token);
            
            // Add edge
            add_edge(g, vertex_id, neighbor_id, weight);
            edges_added++;
            
            state = 1; // Next token should be neighbor ID
        }
        
        token = strtok(NULL, " \t");
    }
    
    return edges_added;
}

// Write graph in Matrix Market format
void write_matrix_market(Graph *g, const char *output_file) {
    FILE *f = fopen(output_file, "w");
    if (!f) {
        fprintf(stderr, "Cannot create output file: %s\n", output_file);
        return;
    }
    
    // Write header
    fprintf(f, "%%%%MatrixMarket matrix coordinate integer symmetric\n");
    
    // Calculate proper dimensions
    int num_nodes = g->max_node_id + 1;
    
    fprintf(f, "%d %d %d\n", num_nodes, num_nodes, g->num_edges);
    
    // Write edges (convert to 1-based indexing)
    for (int i = 0; i < g->num_edges; i++) {
        int from_1based = g->edges[i].from + 1;
        int to_1based = g->edges[i].to + 1;
        
        fprintf(f, "%d %d %d\n", from_1based, to_1based, g->edges[i].weight);
    }
    
    fclose(f);
}

int main(int argc, char **argv) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s input_file output_file\n", argv[0]);
        return 1;
    }
    
    char *input_file = argv[1];
    char *output_file = argv[2];
    
    // Initialize graph
    Graph g;
    init_graph(&g);
    
    // Read input file
    FILE *f = fopen(input_file, "r");
    if (!f) {
        fprintf(stderr, "Cannot open input file: %s\n", input_file);
        return 1;
    }
    
    char line[MAX_LINE_LENGTH];
    while (fgets(line, sizeof(line), f)) {
        parse_line(line, &g);
    }
    fclose(f);
    
    // Write Matrix Market file
    write_matrix_market(&g, output_file);
    
    // Cleanup
    free(g.edges);
    
    return 0;
}