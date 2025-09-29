package com.ancavar.giraph.mst.algorithm;

import com.ancavar.giraph.mst.aggregator.DisjointSetAggregator;
import com.ancavar.giraph.mst.aggregator.MSTAggregator;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
import org.apache.giraph.writable.tuple.IntIntWritable;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.log4j.Logger;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * MST-focused Boruvka's Algorithm implementation that outputs only MST edges.
 * <p>
 * This implementation finds a Minimum Spanning Tree (MST) in a weighted graph
 * using a distributed version of Boruvka's algorithm.
 */
public class MSTBoruvkaComputation extends BasicComputation<
        IntWritable,       // Vertex ID
        NullWritable,     // Vertex Value (not used)
        IntWritable,     // Edge Value (weight)
        IntIntWritable> { // Message Value (source vertex ID and edge weight)

    private static final Logger LOG = Logger.getLogger(MSTBoruvkaComputation.class);

    // Aggregator name constant
    public static final String DISJOINT_SET_AGG = "boruvka.union.find.aggregator";
    public static final String MST_EDGE_AGG = "boruvka.mst.edge.aggregator";

    @Override
    public void compute(
            Vertex<IntWritable, NullWritable, IntWritable> vertex,
            Iterable<IntIntWritable> messages) throws IOException {

        long superstep = getSuperstep();
        int vertexId = vertex.getId().get();

        if (superstep == 0) {
            initializeVertex(vertex);
        } else if (superstep == 1 || superstep % 2 == 0) {
            processComponentMessages(vertex, messages);
        } else {
            broadcastComponentId(vertex, messages);
        }

        vertex.voteToHalt();
    }

    /**
     * Initializes the vertex in the first superstep by adding it to the union-find
     * structure and sending initial messages to neighbors.
     */
    private void initializeVertex(Vertex<IntWritable, NullWritable, IntWritable> vertex) {
        int vertexId = vertex.getId().get();

        // Register this vertex with the union-find aggregator
        DisjointSetAggregator.DisjointSetWritable disjointSet = new DisjointSetAggregator.DisjointSetWritable();
        disjointSet.find(vertexId); // Initialize vertex in disjoint set
        aggregate(DISJOINT_SET_AGG, disjointSet);

        // Send initial messages to all neighbors
        sendMessagesToNeighbors(vertex);

        LOG.info("Superstep 0: Vertex " + vertexId + " registered in union-find and sent initial component to neighbors");
    }

    /**
     * Sends messages to all neighbors with this vertex's ID and the edge weight.
     */
    private void sendMessagesToNeighbors(Vertex<IntWritable, NullWritable, IntWritable> vertex) {
        int vertexId = vertex.getId().get();

        for (Edge<IntWritable, IntWritable> edge : vertex.getEdges()) {
            sendMessage(edge.getTargetVertexId(), new IntIntWritable(vertexId, edge.getValue().get()));
        }
    }

    /**
     * Processes received messages to find the minimum weight edge to a different component,
     * then proposes this edge for inclusion in the MST.
     */
    private void processComponentMessages(
            Vertex<IntWritable, NullWritable, IntWritable> vertex,
            Iterable<IntIntWritable> messages) {

        int vertexId = vertex.getId().get();
        long superstep = getSuperstep();

        LOG.info("Superstep " + superstep + ": Vertex " + vertexId + " processing component messages");

        // Get current component ID from aggregator
        DisjointSetAggregator.DisjointSetWritable disjointSet = getAggregatedValue(DISJOINT_SET_AGG);
        int myComponentId = disjointSet.find(vertexId);

        LOG.debug("Vertex " + vertexId + " current component: " + myComponentId);

        // Find minimum weight edge to a different component
        MinimumEdge minEdge = findMinimumWeightEdge(messages, disjointSet);

        // Propose the minimum edge to the aggregator if found
        if (minEdge.isValid()) {
            LOG.info("Vertex " + vertexId + " proposing edge to " + minEdge.targetId +
                    " (component " + minEdge.targetComponentId + ") with weight " + minEdge.weight);

            MSTAggregator.MSTEdgeSetWritable proposal = new MSTAggregator.MSTEdgeSetWritable();
            proposal.proposeEdge(myComponentId, minEdge.targetComponentId, vertexId, minEdge.targetId, minEdge.weight);
            aggregate(MST_EDGE_AGG, proposal);
        }

        // Mark this component as active
        broadcastComponentId(vertex, messages);
        LOG.debug("Vertex " + vertexId + " marked component as active");
    }

    /**
     * Helper class to track the minimum weight edge during message processing.
     */
    private static class MinimumEdge {
        int weight = Integer.MAX_VALUE;
        int targetId = -1;
        int targetComponentId = -1;

        boolean isValid() {
            return targetId != -1;
        }
    }

    /**
     * Finds the minimum weight edge to a different component from incoming messages.
     */
    private MinimumEdge findMinimumWeightEdge(
            Iterable<IntIntWritable> messages,
            DisjointSetAggregator.DisjointSetWritable disjointSet) {

        MinimumEdge minEdge = new MinimumEdge();

        for (IntIntWritable message : messages) {
            int targetId = message.getLeft().get();
            int weight = message.getRight().get();
            int targetComponentId = disjointSet.find(targetId);

            if (weight < minEdge.weight || (weight == minEdge.weight && targetId < minEdge.targetId)) {
                minEdge.weight = weight;
                minEdge.targetId = targetId;
                minEdge.targetComponentId = targetComponentId;
            }
        }

        return minEdge;
    }

    /**
     * Broadcasts this vertex's component ID to neighboring vertices in different components.
     * If no edges to other components exist, prunes non-MST edges.
     */
    private void broadcastComponentId(
            Vertex<IntWritable, NullWritable, IntWritable> vertex,
            Iterable<IntIntWritable> messages) {

        int vertexId = vertex.getId().get();
        long superstep = getSuperstep();
        DisjointSetAggregator.DisjointSetWritable disjointSet = getAggregatedValue(DISJOINT_SET_AGG);
        int myComponentId = disjointSet.find(vertexId);

        LOG.info("Superstep " + superstep + ": Vertex " + vertexId + " broadcasting component " + myComponentId);

        boolean hasExternalEdges = false;
        for (IntIntWritable message : messages) {
            int targetId = message.getLeft().get();
            int weight = message.getRight().get();
            int targetComponentId = disjointSet.find(targetId);

            if (targetComponentId != myComponentId) {
                hasExternalEdges = true;
                sendMessage(new IntWritable(targetId), new IntIntWritable(vertexId, weight));
                LOG.debug("Vertex " + vertexId + " sent component " + myComponentId + " to vertex " + targetId);
            }
        }

        if (!hasExternalEdges) {
            pruneNonMstEdges(vertex);
        }
    }

    /**
     * Removes edges that are not part of the MST (edges within the same component
     * that are not in the MST edge set).
     */
    private void pruneNonMstEdges(
            Vertex<IntWritable, NullWritable, IntWritable> vertex) {

        DisjointSetAggregator.DisjointSetWritable disjointSet = getAggregatedValue(DISJOINT_SET_AGG);
        MSTAggregator.MSTEdgeSetWritable mst = getAggregatedValue(MST_EDGE_AGG);
        int vertexId = vertex.getId().get();
        LOG.info("Vertex " + vertexId + " has no edges to other components, pruning non-MST edges");

        List<IntWritable> edgesToRemove = new ArrayList<>();
        int myComponentId = disjointSet.find(vertexId);

        for (Edge<IntWritable, IntWritable> edge : vertex.getEdges()) {
            int targetId = edge.getTargetVertexId().get();
            int targetComponentId = disjointSet.find(targetId);

            MSTAggregator.MSTEdge mstEdge = new MSTAggregator.MSTEdge(
                    vertexId, targetId, myComponentId, targetComponentId, edge.getValue().get());
            boolean isInMst = mst.getMSTEdges().contains(mstEdge);

            LOG.info(isInMst + " " + vertexId + " looking for deleting edge to " + targetId +
                    " with weight " + edge.getValue().get());

            if (myComponentId == targetComponentId && !isInMst) {
                edgesToRemove.add(new IntWritable(targetId));
            }
        }

        // Remove all identified non-MST edges
        for (IntWritable id : edgesToRemove) {
            vertex.removeEdges(id);
            LOG.info("Vertex " + vertexId + " removed redundant edge to " + id.get());
        }
    }
}