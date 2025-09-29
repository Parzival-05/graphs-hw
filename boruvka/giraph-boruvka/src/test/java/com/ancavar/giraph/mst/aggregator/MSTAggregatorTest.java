package com.ancavar.giraph.mst.aggregator;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class MSTAggregatorTest {

    private MSTAggregator.MSTEdgeSetWritable mstEdgeSet;

    @BeforeEach
    void setUp() {
        mstEdgeSet = new MSTAggregator.MSTEdgeSetWritable();
    }

    @Test
    void testProposeEdge_NewComponent() {
        mstEdgeSet.proposeEdge(1, 2, 10, 20, 5);
        assertEquals(1, mstEdgeSet.getProposedEdges().size());
    }

    @Test
    void testProposeEdge_BetterWeight() {
        mstEdgeSet.proposeEdge(1, 2, 10, 20, 10);
        mstEdgeSet.proposeEdge(1, 3, 10, 30, 5);

        assertEquals(1, mstEdgeSet.getProposedEdges().size());
        MSTAggregator.MSTEdge edge = mstEdgeSet.getProposedEdges().iterator().next();
        assertEquals(5, edge.getWeight());
        assertEquals(30, edge.getTargetVertexId());
    }

    @Test
    void testAddMSTEdge() {
        MSTAggregator.MSTEdge edge = new MSTAggregator.MSTEdge(1, 2, 1, 2, 5);
        mstEdgeSet.addMSTEdge(edge);

        assertEquals(1, mstEdgeSet.getMSTEdges().size());
        assertTrue(mstEdgeSet.getMSTEdges().contains(edge));
    }

    @Test
    void testClearProposedEdges() {
        mstEdgeSet.proposeEdge(1, 2, 10, 20, 5);
        assertEquals(1, mstEdgeSet.getProposedEdges().size());

        mstEdgeSet.clearProposedEdges();
        assertEquals(0, mstEdgeSet.getProposedEdges().size());
    }

    @Test
    void testMSTEdgeEquals() {
        MSTAggregator.MSTEdge edge1 = new MSTAggregator.MSTEdge(1, 2, 1, 2, 5);
        MSTAggregator.MSTEdge edge2 = new MSTAggregator.MSTEdge(2, 1, 2, 1, 5);

        assertEquals(edge1, edge2); // Should be equal regardless of direction
    }
}