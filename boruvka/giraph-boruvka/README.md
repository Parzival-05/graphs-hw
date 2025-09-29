# Giraph Boruvka MST 
Implementation of Boruvka's algorithm for Minimum Spanning Tree using Apache Giraph in standalone mode (without Hadoop cluster).

## Requirements

- Apache Maven 3.6+
- Java 8
- Apache Giraph 1.3.0 (included as Maven dependency)

## Getting Started

This project runs Giraph in standalone mode without requiring a Hadoop cluster setup.

### Build

```bash
mvn clean compile
mvn package
```

### Run

```bash
java -jar target/giraph-boruvka-1.0-SNAPSHOT.jar

# Or using the Maven exec plugin
mvn exec:java -Dexec.mainClass="com.ancavar.giraph.mst.BoruvkaStarter"
```

## Configuration

The application can be configured through command-line parameters or configuration files:

- **Input file**: Path to the graph file in edge list format
- **Output directory**: Where to write the MST results
- **Number of workers**: For parallel processing (default: based on available cores)

## Input Format

Input files should contain edge lists in the following format:
```
source_vertex_id destination_vertex_id edge_weight
```

**Example input file:**
```
1 2 5
1 3 2
2 3 2
2 4 3
3 4 1
```

This represents a graph where:
- Vertex 1 is connected to vertex 2 with weight 5
- Vertex 1 is connected to vertex 3 with weight 2
- And so on...

## Expected Output

The algorithm outputs edges forming the minimum spanning tree. The output format includes:
- Source vertex ID
- Destination vertex ID  
- Edge weight
- Total weight of the minimum spanning tree

**Example output:**

```
INFO mst.BoruvkaStarter: MST Results:
INFO mst.BoruvkaStarter:   Number of edges: 3
INFO mst.BoruvkaStarter:   Total weight: 5
INFO mst.BoruvkaStarter:   Number of connected components: 1
```

## Development

### Testing
```bash
mvn test

# Run with coverage
mvn test jacoco:report
```

### CI/CD
This project includes GitHub Actions for continuous integration:
- Automatic building and testing on push/PR
- Artifact generation and upload
- Test report generation
