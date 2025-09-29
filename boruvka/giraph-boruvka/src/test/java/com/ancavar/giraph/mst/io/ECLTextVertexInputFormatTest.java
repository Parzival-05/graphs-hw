package com.ancavar.giraph.mst.io;

import org.apache.giraph.edge.Edge;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.NullWritable;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.io.IOException;
import java.util.List;
import java.util.ArrayList;

class ECLTextVertexInputFormatTest {

    @Test
    void testParseVertexWithEdges() throws IOException {
        ECLTextVertexInputFormat format = new ECLTextVertexInputFormat();
        ECLTextVertexInputFormat.ECLVertexReader reader = format.new ECLVertexReader();

        // Test line: "1 2 10 3 20"
        String[] tokens = {"1", "2", "10", "3", "20"};

        IntWritable vertexId = reader.getId(tokens);
        assertEquals(1, vertexId.get());

        NullWritable value = reader.getValue(tokens);
        assertNull(value);

        Iterable<Edge<IntWritable, IntWritable>> edges = reader.getEdges(tokens);
        List<Edge<IntWritable, IntWritable>> edgeList = new ArrayList<>();
        for (Edge<IntWritable, IntWritable> edge : edges) {
            edgeList.add(edge);
        }

        assertEquals(2, edgeList.size());

        // Check first edge: target=2, weight=10
        assertEquals(2, edgeList.get(0).getTargetVertexId().get());
        assertEquals(10, edgeList.get(0).getValue().get());

        // Check second edge: target=3, weight=20
        assertEquals(3, edgeList.get(1).getTargetVertexId().get());
        assertEquals(20, edgeList.get(1).getValue().get());
    }

    @Test
    void testParseVertexWithoutEdges() throws IOException {
        ECLTextVertexInputFormat format = new ECLTextVertexInputFormat();
        ECLTextVertexInputFormat.ECLVertexReader reader = format.new ECLVertexReader();

        // Test line: "5"
        String[] tokens = {"5"};

        IntWritable vertexId = reader.getId(tokens);
        assertEquals(5, vertexId.get());

        Iterable<Edge<IntWritable, IntWritable>> edges = reader.getEdges(tokens);
        List<Edge<IntWritable, IntWritable>> edgeList = new ArrayList<>();
        for (Edge<IntWritable, IntWritable> edge : edges) {
            edgeList.add(edge);
        }

        assertEquals(0, edgeList.size());
    }
}