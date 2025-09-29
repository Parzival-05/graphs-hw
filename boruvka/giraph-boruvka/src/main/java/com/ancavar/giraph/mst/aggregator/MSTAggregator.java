package com.ancavar.giraph.mst.aggregator;

import org.apache.giraph.aggregators.BasicAggregator;
import org.apache.hadoop.io.Writable;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.*;

/**
 * MSTAggregator - Manages a collection of Minimum Spanning Tree edges
 * and proposed edges for Boruvka's algorithm.
 */
public class MSTAggregator extends BasicAggregator<MSTAggregator.MSTEdgeSetWritable> {

    /**
     * Writable implementation for managing MST edges and proposed edges
     */
    public static class MSTEdgeSetWritable implements Writable {
        // Track all edge proposals for final merging decision
        private final Map<Integer, MSTEdge> proposedEdges;

        // Collection of edges selected for the MST
        private final Set<MSTEdge> mstEdges;

        public MSTEdgeSetWritable() {
            proposedEdges = new HashMap<>();
            mstEdges = new HashSet<>();
        }

        /**
         * Propose an edge from component x to component y with weight
         * The edge will only be stored if it's the minimum for component x
         */
        public void proposeEdge(int fromComponentId, int toComponentId,
                                int fromVertexId, int toVertexId, int weight) {

            MSTEdge existingEdge = proposedEdges.get(fromComponentId);
            if (existingEdge == null || weight < existingEdge.weight ||
                    (weight == existingEdge.weight && toVertexId < existingEdge.targetVertexId)) {

                proposedEdges.put(fromComponentId,
                        new MSTEdge(fromVertexId, toVertexId, fromComponentId, toComponentId, weight));
            }
        }

        /**
         * Get all proposed edges
         */
        public Collection<MSTEdge> getProposedEdges() {
            return proposedEdges.values();
        }

        /**
         * Clear all proposed edges after processing
         */
        public void clearProposedEdges() {
            proposedEdges.clear();
        }

        /**
         * Add an edge to the MST
         */
        public void addMSTEdge(MSTEdge edge) {
            mstEdges.add(edge);
        }

        /**
         * Get all MST edges
         */
        public Set<MSTEdge> getMSTEdges() {
            return mstEdges;
        }

        @Override
        public void write(DataOutput out) throws IOException {
            out.writeInt(proposedEdges.size());
            for (Map.Entry<Integer, MSTEdge> entry : proposedEdges.entrySet()) {
                out.writeInt(entry.getKey());
                entry.getValue().write(out);
            }

            out.writeInt(mstEdges.size());
            for (MSTEdge edge : mstEdges) {
                edge.write(out);
            }
        }

        @Override
        public void readFields(DataInput in) throws IOException {
            int edgesSize = in.readInt();
            proposedEdges.clear();
            for (int i = 0; i < edgesSize; i++) {
                int componentId = in.readInt();
                MSTEdge edge = new MSTEdge();
                edge.readFields(in);
                proposedEdges.put(componentId, edge);
            }

            int mstEdgesSize = in.readInt();
            mstEdges.clear();
            for (int i = 0; i < mstEdgesSize; i++) {
                MSTEdge edge = new MSTEdge();
                edge.readFields(in);
                mstEdges.add(edge);
            }
        }
    }

    /**
     * Represents an edge in the MST
     */
    public static class MSTEdge implements Writable {
        private int sourceVertexId;
        private int targetVertexId;
        private int sourceComponentId;
        private int targetComponentId;
        private int weight;

        public MSTEdge() {
        }

        public MSTEdge(int sourceVertexId, int targetVertexId,
                       int sourceComponentId, int targetComponentId, int weight) {
            this.sourceVertexId = sourceVertexId;
            this.targetVertexId = targetVertexId;
            this.sourceComponentId = sourceComponentId;
            this.targetComponentId = targetComponentId;
            this.weight = weight;
        }

        public int getSourceVertexId() {
            return sourceVertexId;
        }

        public int getTargetVertexId() {
            return targetVertexId;
        }

        public int getSourceComponentId() {
            return sourceComponentId;
        }

        public int getTargetComponentId() {
            return targetComponentId;
        }

        public int getWeight() {
            return weight;
        }

        @Override
        public void write(DataOutput out) throws IOException {
            out.writeInt(sourceVertexId);
            out.writeInt(targetVertexId);
            out.writeInt(sourceComponentId);
            out.writeInt(targetComponentId);
            out.writeInt(weight);
        }

        @Override
        public void readFields(DataInput in) throws IOException {
            sourceVertexId = in.readInt();
            targetVertexId = in.readInt();
            sourceComponentId = in.readInt();
            targetComponentId = in.readInt();
            weight = in.readInt();
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            MSTEdge edge = (MSTEdge) o;
            return Double.compare(edge.weight, weight) == 0 &&
                    ((sourceVertexId == edge.sourceVertexId && targetVertexId == edge.targetVertexId) ||
                            (sourceVertexId == edge.targetVertexId && targetVertexId == edge.sourceVertexId));
        }

        @Override
        public int hashCode() {
            // Handle vertex IDs in an order-agnostic way
            int vertexMin = Math.min(sourceVertexId, targetVertexId);
            int vertexMax = Math.max(sourceVertexId, targetVertexId);
            int vertexHash = Integer.hashCode(vertexMin) ^ Integer.hashCode(vertexMax);

            // Combine with weight hash code
            return 31 * vertexHash + Double.hashCode(weight);
        }

        @Override
        public String toString() {
            return "Edge[" + sourceVertexId + "->" + targetVertexId +
                    " (components " + sourceComponentId + "->" + targetComponentId +
                    ", weight=" + weight + ")]";
        }
    }

    @Override
    public MSTEdgeSetWritable createInitialValue() {
        return new MSTEdgeSetWritable();
    }

    @Override
    public void aggregate(MSTEdgeSetWritable value) {
        MSTEdgeSetWritable current = getAggregatedValue();

        // Add proposed edges
        for (MSTEdge edge : value.getProposedEdges()) {
            current.proposeEdge(
                    edge.getSourceComponentId(),
                    edge.getTargetComponentId(),
                    edge.getSourceVertexId(),
                    edge.getTargetVertexId(),
                    edge.getWeight()
            );
        }

        // Add MST edges (if any)
        for (MSTEdge edge : value.getMSTEdges()) {
            current.addMSTEdge(edge);
        }
    }
}