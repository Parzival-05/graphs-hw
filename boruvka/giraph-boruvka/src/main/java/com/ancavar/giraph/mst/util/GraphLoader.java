package com.ancavar.giraph.mst.util;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

/**
 * Utility class for loading graph data from files or resources
 */
public class GraphLoader {

    /**
     * Load graph from classpath resource
     */
    public static String[] loadFromResource(String resourcePath) throws IOException {
        InputStream inputStream = GraphLoader.class.getClassLoader().getResourceAsStream(resourcePath);
        if (inputStream == null) {
            throw new IOException("Resource not found: " + resourcePath);
        }

        List<String> lines = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line.trim());
            }
        }

        return lines.toArray(new String[0]);
    }

    /**
     * Load graph from file path
     */
    public static String[] loadFromFile(String filePath) throws IOException {
        List<String> lines = Files.readAllLines(Paths.get(filePath));
        return lines.toArray(new String[0]);
    }
}
