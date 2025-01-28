package com.example;

import com.machinezoo.sourceafis.FingerprintMatcher;
import com.machinezoo.sourceafis.FingerprintTemplate;
import com.machinezoo.sourceafis.FingerprintImage;
import com.machinezoo.sourceafis.FingerprintImageOptions;

import java.io.FileWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.DirectoryStream;
import java.util.ArrayList;
import java.util.List;

public class MatchingGenuine {
    public static void main(String[] args) {
        // Define a threshold value (it won't matter since we are treating all as genuine)
        double threshold = 0.0;

        List<Double> genuineScores = new ArrayList<>();

        try {
            // Load the probe fingerprint image and create a template (index_11.png is the genuine template)
            FingerprintTemplate probe = new FingerprintTemplate(
                new FingerprintImage(
                    Files.readAllBytes(Paths.get("index_probe_112.png")),
                    new FingerprintImageOptions().dpi(500)
                )
            );

            // Specify the directory containing fingerprint files
            String directoryPath = "/home/chai/sourceafis-project/sourceafis-project/ProbeFingerprint_500_DPI/";

            // Use DirectoryStream to iterate through files in the directory
            try (DirectoryStream<Path> directoryStream = Files.newDirectoryStream(Paths.get(directoryPath))) {
                for (Path filePath : directoryStream) {
                    // Only process files with .png extension
                    if (filePath.toString().endsWith(".png")) {
                        // Load the candidate fingerprint image and create a template
                        try {
                            FingerprintTemplate candidate = new FingerprintTemplate(
                                new FingerprintImage(
                                    Files.readAllBytes(filePath),
                                    new FingerprintImageOptions().dpi(500)
                                )
                            );

                            // Match the templates
                            FingerprintMatcher matcher = new FingerprintMatcher(probe);
                            double score = matcher.match(candidate);

                            // Print the similarity score for each candidate
                            System.out.println("Comparing with " + filePath.getFileName());
                            System.out.println("Similarity score: " + score);
                            System.out.println("-------------------------------");

                            // Add the score to genuine scores regardless of the value
                            genuineScores.add(score);
                            
                        } catch (Exception e) {
                            System.out.println("Error processing file: " + filePath.getFileName());
                            e.printStackTrace();
                        }
                    }
                }
            }

            // Compare the genuine probe against itself to create genuine scores
            double selfMatchScore = new FingerprintMatcher(probe).match(probe);
            genuineScores.add(selfMatchScore);

            // Save the scores to a CSV file
            saveScoresToCSV(genuineScores);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void saveScoresToCSV(List<Double> genuineScores) {
        try (FileWriter writer = new FileWriter("scoresGenuine.csv")) {
            writer.write("Score,Label\n");

            // Write all scores as genuine
            for (double score : genuineScores) {
                writer.write(score + ",genuine\n");
            }

            System.out.println("Scores saved to scoresGenuine.csv");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
