package com.ancavar.giraph.mst.algorithm;

import com.ancavar.giraph.mst.aggregator.DisjointSetAggregator;
import com.ancavar.giraph.mst.aggregator.MSTAggregator;
import org.apache.giraph.master.DefaultMasterCompute;
import org.apache.log4j.Logger;

import static com.ancavar.giraph.mst.algorithm.MSTBoruvkaComputation.DISJOINT_SET_AGG;
import static com.ancavar.giraph.mst.algorithm.MSTBoruvkaComputation.MST_EDGE_AGG;

/**
 * Master compute class for coordinating the algorithm
 */
public class MSTBoruvkaMasterCompute extends DefaultMasterCompute {
    private static final Logger LOG = Logger.getLogger(MSTBoruvkaComputation.class);

    @Override
    public void initialize() throws InstantiationException, IllegalAccessException {
        registerPersistentAggregator(DISJOINT_SET_AGG, DisjointSetAggregator.class);
        registerPersistentAggregator(MST_EDGE_AGG, MSTAggregator.class);
    }

    @Override
    public void compute() {
        long superstep = getSuperstep();

        // Skip processing for superstep 0 (initialization)
        if (superstep == 0) {
            LOG.info("Superstep 0 MasterCompute");
            return;
        }

        // On odd supersteps, process the aggregated edge proposals and perform merges
        if (superstep % 2 == 1) {
            DisjointSetAggregator.DisjointSetWritable disjointSet =
                    getAggregatedValue(DISJOINT_SET_AGG);
            MSTAggregator.MSTEdgeSetWritable mst = getAggregatedValue(MST_EDGE_AGG);

            int numComponents = disjointSet.getNumComponents();

            // If no active components or only one component remains, we're done
            if (numComponents <= 1) {
                LOG.info("Algorithm converged with " + numComponents + " components");
                LOG.info("MST has " + mst.getMSTEdges().size() + " edges");
                haltComputation();
                return;
            }

            // Process all proposed edges and perform merges
            for (MSTAggregator.MSTEdge edge : mst.getProposedEdges()) {
                int sourceComp = edge.getSourceComponentId();
                int targetComp = edge.getTargetComponentId();

                // Find current component IDs with path compression
                int currentSourceComp = disjointSet.find(sourceComp);
                int currentTargetComp = disjointSet.find(targetComp);

                // Skip if components are already merged
                if (currentSourceComp == currentTargetComp) {
                    continue;
                }

                LOG.info("Adding MST edge: " + edge.getSourceVertexId() + " -> " +
                        edge.getTargetVertexId() + " weight " + edge.getWeight());

                // Add edge to MST
                mst.addMSTEdge(edge);

                // Merge components
                disjointSet.union(currentSourceComp, currentTargetComp);
            }

            // Clear edge proposals for next iteration
            mst.clearProposedEdges();
            setAggregatedValue(DISJOINT_SET_AGG, disjointSet);
        }
    }
}