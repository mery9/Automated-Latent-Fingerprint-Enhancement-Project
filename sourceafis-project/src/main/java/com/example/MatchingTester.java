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

public class MatchingTester {
    public static void main(String[] args) {
        // Define a threshold value (can be ignored since everything is impostor)
        double threshold = 0.0; // Adjust this value if necessary

        List<Double> impostorScores = new ArrayList<>();

        try {
            FingerprintTemplate probe = new FingerprintTemplate(
                new FingerprintImage(
                    Files.readAllBytes(Paths.get("/home/chai/sourceafis-project/sourceafis-project/Exemplar/B129T7U.png")),
                    new FingerprintImageOptions().dpi(500)
                )
            );

            // Specify the directory containing fingerprint files
            String directoryPath = "/home/chai/sourceafis-project/sourceafis-project/Latent";

            // Use DirectoryStream to iterate through files in the directory
            try (DirectoryStream<Path> directoryStream = Files.newDirectoryStream(Paths.get(directoryPath))) {
                for (Path filePath : directoryStream) {
                    // Only process files with .png extension
                    if (filePath.toString().endsWith(".tif") || filePath.toString().endsWith(".png")) {
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

                            // Since everything is impostor, add the score to impostorScores
                            impostorScores.add(score);

                        } catch (Exception e) {
                            System.out.println("Error processing file: " + filePath.getFileName());
                            e.printStackTrace();
                        }
                    }
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

}