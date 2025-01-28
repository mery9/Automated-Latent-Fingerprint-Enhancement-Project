package com.example;

import com.machinezoo.sourceafis.FingerprintMatcher;
import com.machinezoo.sourceafis.FingerprintTemplate;
import com.machinezoo.sourceafis.FingerprintImage;
import com.machinezoo.sourceafis.FingerprintImageOptions;

import javax.swing.*;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.DirectoryStream;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import javax.imageio.ImageIO;

public class IdentificationSystem {
    public static void main(String[] args) {
        List<MatchResult> matchResults = new ArrayList<>();

        try {
            // Load the probe fingerprint image and create a template
            FingerprintTemplate probe = new FingerprintTemplate(
                new FingerprintImage(
                    Files.readAllBytes(Paths.get("/home/chai/sourceafis-project/sourceafis-project/Latent/G051L6U.png")),
                    new FingerprintImageOptions().dpi(500)
                )
            );

            // Specify the directory containing fingerprint files

            // String directoryPath = "/home/chai/sourceafis-project/sourceafis-project/ProbeFingerprint_500_DPI/";
            // String directoryPath = "/home/chai/sourceafis-project/sourceafis-project/ImposterFingerprint/";

            // String directoryPath = "/home/chai/sourceafis-project/sourceafis-project/Latent";
            String directoryPath = "/home/chai/sourceafis-project/sourceafis-project/Exemplar";

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

                            // Store the score and file path
                            matchResults.add(new MatchResult(score, filePath));

                        } catch (Exception e) {
                            System.out.println("Error processing file: " + filePath.getFileName());
                            e.printStackTrace();
                        }
                    }
                }
            }

            // Sort results by score in descending order and take the top 15
            matchResults.sort(Comparator.comparingDouble(MatchResult::getScore).reversed());
            List<MatchResult> top15Matches = matchResults.subList(0, Math.min(15, matchResults.size()));

            // Display top 15 matches in a GUI
            JFrame frame = displayTopMatches(top15Matches);

            // Save the UI to an image file
            saveFrameAsImage(frame, "IdentificationOutput.png");

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Helper class to store match results
    private static class MatchResult {
        private final double score;
        private final Path filePath;

        public MatchResult(double score, Path filePath) {
            this.score = score;
            this.filePath = filePath;
        }

        public double getScore() {
            return score;
        }

        public Path getFilePath() {
            return filePath;
        }
    }

    // Method to display the top 10 matches in a GUI
    private static JFrame displayTopMatches(List<MatchResult> topMatches) {
        JFrame frame = new JFrame("Top 10 Fingerprint Matches");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(1200, 800);
    
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
    
        int totalHeight = 0; // Track total height of the panel dynamically
    
        for (MatchResult match : topMatches) {
            try {
                BufferedImage image = ImageIO.read(match.getFilePath().toFile());
    
                JLabel imageLabel = new JLabel(new ImageIcon(image));
                imageLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
    
                JLabel filenameLabel = new JLabel("File: " + match.getFilePath().getFileName().toString());
                filenameLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
                JLabel scoreLabel = new JLabel(String.format("Score: %.2f", match.getScore()));
                scoreLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
    
                JPanel imagePanel = new JPanel();
                imagePanel.setLayout(new BoxLayout(imagePanel, BoxLayout.Y_AXIS));
                imagePanel.add(imageLabel);
                imagePanel.add(filenameLabel);
                imagePanel.add(scoreLabel);
    
                imagePanel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5));
                panel.add(imagePanel);
    
                // Dynamically add each component's height to totalHeight
                totalHeight += image.getHeight() + filenameLabel.getPreferredSize().height 
                               + scoreLabel.getPreferredSize().height + 20; // Extra padding
    
            } catch (IOException e) {
                System.out.println("Error loading image: " + match.getFilePath());
                e.printStackTrace();
            }
        }
    
        // Set the calculated height as the preferred size for the panel
        panel.setPreferredSize(new Dimension(1200, totalHeight));
    
        JScrollPane scrollPane = new JScrollPane(panel);
        scrollPane.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
        scrollPane.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
    
        frame.add(scrollPane);
    
        panel.revalidate();
        panel.repaint();
        frame.revalidate();
        frame.repaint();
        frame.setVisible(true);
    
        return frame;
    }
    
    
    

    // Method to save the frame as an image file
    private static void saveFrameAsImage(JFrame frame, String fileName) {
        try {
            // Get the scroll pane and the panel it contains
            JScrollPane scrollPane = (JScrollPane) frame.getContentPane().getComponent(0);
            JPanel panel = (JPanel) scrollPane.getViewport().getView();

            // Create an image with the full height of the panel
            Dimension panelSize = panel.getPreferredSize();
            BufferedImage image = new BufferedImage(panelSize.width, panelSize.height, BufferedImage.TYPE_INT_ARGB);
            
            // Render the entire panel onto the BufferedImage
            Graphics2D graphics = image.createGraphics();
            panel.paint(graphics);
            graphics.dispose();

            // Save the BufferedImage to a file
            ImageIO.write(image, "png", new File(fileName));
            System.out.println("UI saved as " + fileName);

        } catch (IOException e) {
            System.out.println("Error saving the UI as an image.");
            e.printStackTrace();
        }
    }
}
