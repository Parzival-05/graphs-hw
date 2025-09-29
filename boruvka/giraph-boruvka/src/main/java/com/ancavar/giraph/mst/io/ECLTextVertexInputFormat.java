package com.ancavar.giraph.mst.io;

import org.apache.giraph.edge.Edge;
import org.apache.giraph.edge.EdgeFactory;
import org.apache.giraph.io.formats.TextVertexInputFormat;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.InputSplit;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

import java.io.IOException;
import java.util.regex.Pattern;

/**
 * Simple text-based vertex input format for ECL-based graph.
 *
 * Format:
 * vertex_id neighbor1_id weight1 neighbor2_id weight2 ...
 *
 * Example:
 * 0 1 5.0 2 10.0
 * 1 2 7.0
 * 2
 *
 */
public class ECLTextVertexInputFormat extends
        TextVertexInputFormat<IntWritable, NullWritable, IntWritable> {

    // Split by whitespace
    private static final Pattern SEPARATOR = Pattern.compile("\\s+");

    @Override
    public TextVertexReader createVertexReader(InputSplit split,
                                               TaskAttemptContext context) {
        return new ECLVertexReader();
    }

    /**
     * Vertex reader for ECL text format.
     */
    public class ECLVertexReader extends
            TextVertexReaderFromEachLineProcessed<String[]> {

        @Override
        protected String[] preprocessLine(Text line) throws IOException {
            return SEPARATOR.split(line.toString());
        }

        @Override
        protected IntWritable getId(String[] tokens) throws IOException {
            return new IntWritable(Integer.parseInt(tokens[0]));
        }

        @Override
        protected NullWritable getValue(String[] tokens) throws IOException {
            // Default vertex value is 1.0
            return null;
        }

        @Override
        protected Iterable<Edge<IntWritable, IntWritable>> getEdges(
                String[] tokens) throws IOException {
            // If there are no edges for this vertex
            if (tokens.length <= 1) {
                return java.util.Collections.emptyList();
            }

            // Build the edge list
            java.util.List<Edge<IntWritable, IntWritable>> edges =
                    new java.util.ArrayList<>();

            // Parse pairs of (target_id, weight)
            // Format: source_id target1_id weight1 target2_id weight2 ...
            for (int i = 1; i < tokens.length; i += 2) {
                int targetId = Integer.parseInt(tokens[i]);
                int weight = Integer.parseInt(tokens[i + 1]);
                edges.add(EdgeFactory.create(
                        new IntWritable(targetId), new IntWritable(weight)));
            }

            return edges;
        }
    }
}