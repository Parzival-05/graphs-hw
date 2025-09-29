package com.ancavar.giraph.mst;

import com.ancavar.giraph.mst.algorithm.MSTBoruvkaComputation;
import com.ancavar.giraph.mst.algorithm.MSTBoruvkaMasterCompute;
import com.ancavar.giraph.mst.io.ECLTextVertexInputFormat;
import com.ancavar.giraph.mst.io.ECLTextVertexOutputFormat;
import com.ancavar.giraph.mst.util.GraphLoader;
import com.ancavar.giraph.mst.util.MSTEdgeUtils;
import org.apache.giraph.conf.GiraphConfiguration;
import org.apache.giraph.utils.InternalVertexRunner;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Set;

/**
 * Starter class to run MST Boruvka algorithm locally in JVM without Hadoop cluster
 */
public class BoruvkaStarter {

    private static final Logger logger = LoggerFactory.getLogger(BoruvkaStarter.class);

    public static void main(String[] args) throws Exception {
        logger.info("Starting MST Boruvka algorithm in JVM mode...");

        String inputFile = null;
        int numRuns = 1;

        // Parse command line arguments
        for (int i = 0; i < args.length; i++) {
            if ("-n".equals(args[i]) && i + 1 < args.length) {
                numRuns = Integer.parseInt(args[i + 1]);
                i++; // Skip next argument as it's the value
            } else if (!args[i].startsWith("-")) {
                inputFile = args[i]; // Input file (no flag)
            }
        }

        if (inputFile == null) {
            throw new IllegalArgumentException("Please provide the input graph file path as an argument.");
        }

        logger.info("Reading graph from file: {}", inputFile);
        String[] graphData = GraphLoader.loadFromFile(inputFile);

        GiraphConfiguration conf = new GiraphConfiguration();
        conf.setComputationClass(MSTBoruvkaComputation.class);
        conf.setVertexInputFormatClass(ECLTextVertexInputFormat.class);
        conf.setVertexOutputFormatClass(ECLTextVertexOutputFormat.class);
        conf.setMasterComputeClass(MSTBoruvkaMasterCompute.class);
        conf.setNumComputeThreads(8);
        // logger.info("Input graph ({} vertices):", graphData.length);
        // for (String line : graphData) {
        //     logger.info("  {}", line);
        // }

        // Benchmark runs
        logger.info("Running {} benchmark runs...", numRuns);
        Set<MSTEdgeUtils.MSTEdge> mstEdges = null;
        int totalWeight = 0;
        
        for (int run = 0; run < numRuns; run++) {
            logger.info("Benchmark run {}/{}", run + 1, numRuns);
            Iterable<String> results = InternalVertexRunner.run(conf, graphData);
            
            // Store results from last run
            mstEdges = MSTEdgeUtils.parseMSTEdges(results);
            totalWeight = MSTEdgeUtils.getTotalWeight(mstEdges);
        }

        logger.info("MST Results:");
        logger.info("  Number of edges: {}", mstEdges.size());
        logger.info("  Total weight: {}", totalWeight);
        // logger.info("  MST edges:");
        // for (MSTEdgeUtils.MSTEdge edge : mstEdges) {
        //     logger.info("    {}", edge);
        // }

        logger.info("Completed successfully!");
    }
}
