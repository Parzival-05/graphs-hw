package com.ancavar.giraph.mst.aggregator;

import org.apache.giraph.aggregators.BasicAggregator;
import org.apache.hadoop.io.Writable;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * DisjointSetAggregator - Manages a disjoint-set structure for tracking
 * component membership in Boruvka's algorithm.
 */
public class DisjointSetAggregator
        extends BasicAggregator<DisjointSetAggregator.DisjointSetWritable> {

    /**
     * Writable implementation of a disjoint-set data structure
     * for component tracking in Boruvka's algorithm
     */
    public static class DisjointSetWritable implements Writable {
        // Maps vertex ID to its parent in the disjoint set
        private final Map<Integer, Integer> parent;

        // Track component sizes for path compression optimization
        private final Map<Integer, Integer> size;

        public DisjointSetWritable() {
            parent = new HashMap<>();
            size = new HashMap<>();
        }

        /**
         * Find the component ID (root) for a vertex with path compression
         */
        public int find(int x) {
            if (!parent.containsKey(x)) {
                parent.put(x, x);
                size.put(x, 1);
                return x;
            }

            if (parent.get(x) != x) {
                parent.put(x, find(parent.get(x)));
            }
            return parent.get(x);
        }

        /**
         * Union two components by rank (size)
         */
        public void union(int x, int y) {
            int rootX = find(x);
            int rootY = find(y);

            if (rootX == rootY) return;

            // Union by rank - attach smaller tree under root of larger tree
            if (size.get(rootX) < size.get(rootY)) {
                parent.put(rootX, rootY);
                size.put(rootY, size.get(rootY) + size.get(rootX));
            } else {
                parent.put(rootY, rootX);
                size.put(rootX, size.get(rootX) + size.get(rootY));
            }
        }

        /**
         * Get all component IDs (roots)
         */
        public Set<Integer> getComponentIds() {
            Set<Integer> components = new HashSet<>();
            for (Integer vertex : parent.keySet()) {
                components.add(find(vertex));
            }
            return components;
        }

        /**
         * Get number of distinct components
         */
        public int getNumComponents() {
            return getComponentIds().size();
        }

        @Override
        public void write(DataOutput out) throws IOException {
            out.writeInt(parent.size());
            for (Map.Entry<Integer, Integer> entry : parent.entrySet()) {
                out.writeInt(entry.getKey());
                out.writeInt(entry.getValue());
            }

            out.writeInt(size.size());
            for (Map.Entry<Integer, Integer> entry : size.entrySet()) {
                out.writeInt(entry.getKey());
                out.writeInt(entry.getValue());
            }
        }

        @Override
        public void readFields(DataInput in) throws IOException {
            int parentSize = in.readInt();
            parent.clear();
            for (int i = 0; i < parentSize; i++) {
                parent.put(in.readInt(), in.readInt());
            }

            int sizeMapSize = in.readInt();
            size.clear();
            for (int i = 0; i < sizeMapSize; i++) {
                size.put(in.readInt(), in.readInt());
            }
        }
    }

    @Override
    public DisjointSetWritable createInitialValue() {
        return new DisjointSetWritable();
    }

    @Override
    public void aggregate(DisjointSetWritable value) {
        DisjointSetWritable current = getAggregatedValue();

        // Merge parent maps (need to recompute roots after all updates)
        for (Map.Entry<Integer, Integer> entry : value.parent.entrySet()) {
            int vertex = entry.getKey();
            int parent = entry.getValue();

            if (!current.parent.containsKey(vertex)) {
                current.parent.put(vertex, parent);
                current.size.put(vertex, value.size.getOrDefault(vertex, 1));
            }
        }
    }
}