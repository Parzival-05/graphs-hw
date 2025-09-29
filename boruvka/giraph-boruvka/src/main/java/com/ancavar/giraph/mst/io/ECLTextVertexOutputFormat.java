package com.ancavar.giraph.mst.io;

import org.apache.giraph.graph.Vertex;
import org.apache.giraph.io.formats.TextVertexOutputFormat;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.NullWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.TaskAttemptContext;

import java.io.IOException;

/**
 * Simple output format that outputs vertex information.
 * MST edges should be extracted from aggregators in the test.
 */
public class ECLTextVertexOutputFormat extends
        TextVertexOutputFormat<IntWritable, NullWritable, IntWritable> {

    @Override
    public TextVertexWriter createVertexWriter(TaskAttemptContext context)
            throws IOException, InterruptedException {
        return new ECLVertexWriter();
    }

    protected class ECLVertexWriter extends TextVertexWriterToEachLine {

        @Override
        protected Text convertVertexToLine(
                Vertex<IntWritable, NullWritable, IntWritable> vertex)
                throws IOException {

            StringBuilder sb = new StringBuilder();
            sb.append(vertex.getId().get());

            // Output edges for debugging/verification
            for (org.apache.giraph.edge.Edge<IntWritable, IntWritable> edge : vertex.getEdges()) {
                sb.append(" ").append(edge.getTargetVertexId().get())
                        .append(" ").append(edge.getValue().get());
            }

            return new Text(sb.toString());
        }
    }
}