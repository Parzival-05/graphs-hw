package com.ancavar.giraph.mst.aggregator;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class DisjointSetAggregatorTest {

    private DisjointSetAggregator.DisjointSetWritable disjointSet;

    @BeforeEach
    void setUp() {
        disjointSet = new DisjointSetAggregator.DisjointSetWritable();
    }

    @Test
    void testFind_NewVertex() {
        int result = disjointSet.find(1);
        assertEquals(1, result);
    }

    @Test
    void testUnion_TwoVertices() {
        disjointSet.find(1);
        disjointSet.find(2);
        disjointSet.union(1, 2);

        int root1 = disjointSet.find(1);
        int root2 = disjointSet.find(2);
        assertEquals(root1, root2);
    }

    @Test
    void testGetNumComponents() {
        disjointSet.find(1);
        disjointSet.find(2);
        disjointSet.find(3);
        assertEquals(3, disjointSet.getNumComponents());

        disjointSet.union(1, 2);
        assertEquals(2, disjointSet.getNumComponents());
    }

    @Test
    void testPathCompression() {
        disjointSet.find(1);
        disjointSet.find(2);
        disjointSet.find(3);
        disjointSet.union(1, 2);
        disjointSet.union(2, 3);

        // After path compression, all should point to same root
        int root = disjointSet.find(3);
        assertEquals(root, disjointSet.find(1));
        assertEquals(root, disjointSet.find(2));
    }
}