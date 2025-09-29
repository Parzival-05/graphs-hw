package com.ancavar.giraph.mst.util;

import java.util.HashSet;
import java.util.Set;

/**
 * Utility class for parsing and handling MST edges from Giraph output
 */
public class MSTEdgeUtils {

    public static class MSTEdge {
        public final int source, target, weight;

        public MSTEdge(int source, int target, int weight) {
            // Normalize edge direction for comparison
            this.source = Math.min(source, target);
            this.target = Math.max(source, target);
            this.weight = weight;
        }

        @Override
        public boolean equals(Object obj) {
            if (!(obj instanceof MSTEdge)) return false;
            MSTEdge other = (MSTEdge) obj;
            return source == other.source && target == other.target && weight == other.weight;
        }

        @Override
        public int hashCode() {
            return source * 31 + target * 37 + weight;
        }

        @Override
        public String toString() {
            return String.format("(%d-%d, w=%d)", source, target, weight);
        }
    }

    public static Set<MSTEdge> parseMSTEdges(Iterable<String> results) {
        Set<MSTEdge> edges = new HashSet<>();

        // Handle null results (e.g., single vertex with no edges)
        if (results == null) {
            return edges;
        }

        for (String line : results) {
            // Skip null or empty lines
            if (line == null || line.trim().isEmpty()) {
                continue;
            }

            String[] parts = line.trim().split("\\s+");
            if (parts.length >= 3) {
                int sourceVertex = Integer.parseInt(parts[0]);

                // Parse edges in pairs: target, weight, target, weight, ...
                for (int i = 1; i < parts.length; i += 2) {
                    if (i + 1 < parts.length) {
                        int targetVertex = Integer.parseInt(parts[i]);
                        int weight = Integer.parseInt(parts[i + 1]);

                        // Only add edge once (MSTEdge constructor handles normalization)
                        if (sourceVertex < targetVertex) {
                            edges.add(new MSTEdge(sourceVertex, targetVertex, weight));
                        }
                    }
                }
            }
        }
        return edges;
    }

    public static boolean containsEdge(Set<MSTEdge> edges, int source, int target, int weight) {
        return edges.contains(new MSTEdge(source, target, weight));
    }

    public static int getTotalWeight(Set<MSTEdge> edges) {
        return edges.stream().mapToInt(e -> e.weight).sum();
    }
}
