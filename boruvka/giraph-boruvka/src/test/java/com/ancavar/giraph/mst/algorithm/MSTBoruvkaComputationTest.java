package com.ancavar.giraph.mst.algorithm;

import com.ancavar.giraph.mst.io.ECLTextVertexInputFormat;
import com.ancavar.giraph.mst.io.ECLTextVertexOutputFormat;
import com.ancavar.giraph.mst.util.GraphLoader;
import com.ancavar.giraph.mst.util.MSTEdgeUtils;
import org.apache.giraph.conf.GiraphConfiguration;
import org.apache.giraph.utils.InternalVertexRunner;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests for {@link MSTBoruvkaComputation}
 */
class MSTBoruvkaComputationTest {

    private GiraphConfiguration conf;

    @BeforeEach
    void setUp() {
        conf = new GiraphConfiguration();
        conf.setComputationClass(MSTBoruvkaComputation.class);
        conf.setVertexInputFormatClass(ECLTextVertexInputFormat.class);
        conf.setVertexOutputFormatClass(ECLTextVertexOutputFormat.class);
        conf.setMasterComputeClass(MSTBoruvkaMasterCompute.class);
    }

    @Test
    void testToyData() throws Exception {
        String[] graph = GraphLoader.loadFromResource("test-graphs/triangle.txt");

        Iterable<String> results = InternalVertexRunner.run(conf, graph);
        Set<MSTEdgeUtils.MSTEdge> mstEdges = MSTEdgeUtils.parseMSTEdges(results);

        assertEquals(2, mstEdges.size(), "Triangle MST should have exactly 2 edges");

        // Expected MST edges: (2,3,5) and (1,3,6) with total weight 11
        assertTrue(MSTEdgeUtils.containsEdge(mstEdges, 2, 3, 5), "Should contain edge 2-3 with weight 5");
        assertTrue(MSTEdgeUtils.containsEdge(mstEdges, 1, 3, 6), "Should contain edge 1-3 with weight 6");

        int totalWeight = MSTEdgeUtils.getTotalWeight(mstEdges);
        assertEquals(11, totalWeight, "Total MST weight should be 11");
    }

    @Test
    void testLargerGraph() throws Exception {
        String[] graph = GraphLoader.loadFromResource("test-graphs/larger-graph.txt");

        Iterable<String> results = InternalVertexRunner.run(conf, graph);
        Set<MSTEdgeUtils.MSTEdge> mstEdges = MSTEdgeUtils.parseMSTEdges(results);

        assertEquals(3, mstEdges.size(), "4-vertex MST should have exactly 3 edges");

        // Expected MST: edges (2,3,1), (1,3,2), (2,4,5) with total weight 8
        assertTrue(MSTEdgeUtils.containsEdge(mstEdges, 2, 3, 1), "Should contain edge 2-3 with weight 1");
        assertTrue(MSTEdgeUtils.containsEdge(mstEdges, 1, 3, 2), "Should contain edge 1-3 with weight 2");

        int totalWeight = MSTEdgeUtils.getTotalWeight(mstEdges);
        assertEquals(8, totalWeight, "Total MST weight should be 8");
    }

    @Test
    void testSingleVertex() throws Exception {
        String[] graph = GraphLoader.loadFromResource("test-graphs/single-vertex.txt");

        Iterable<String> results = InternalVertexRunner.run(conf, graph);
        Set<MSTEdgeUtils.MSTEdge> mstEdges = MSTEdgeUtils.parseMSTEdges(results);

        assertEquals(0, mstEdges.size(), "Single vertex should have no edges in MST");
    }

    @Test
    void testDisconnectedGraph() throws Exception {
        String[] graph = GraphLoader.loadFromResource("test-graphs/disconnected.txt");

        Iterable<String> results = InternalVertexRunner.run(conf, graph);
        Set<MSTEdgeUtils.MSTEdge> mstEdges = MSTEdgeUtils.parseMSTEdges(results);

        // Two disconnected components, each with 1 edge
        assertEquals(2, mstEdges.size(), "Disconnected graph should have 2 MST edges");

        assertTrue(MSTEdgeUtils.containsEdge(mstEdges, 1, 2, 5), "Should contain edge 1-2 with weight 5");
        assertTrue(MSTEdgeUtils.containsEdge(mstEdges, 3, 4, 3), "Should contain edge 3-4 with weight 3");
    }
}