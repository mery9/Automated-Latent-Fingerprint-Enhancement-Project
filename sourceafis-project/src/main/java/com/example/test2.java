package com.example;

import com.machinezoo.sourceafis.FingerprintMatcher;
import com.machinezoo.sourceafis.FingerprintTemplate;
import com.machinezoo.sourceafis.FingerprintImage;
import com.machinezoo.sourceafis.FingerprintImageOptions;
import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.plot.XYPlot;
import org.jfree.chart.renderer.xy.XYLineAndShapeRenderer;
import org.jfree.data.xy.XYSeries;
import org.jfree.data.xy.XYSeriesCollection;

import javax.swing.*;
import java.awt.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class test2 {
    public static void main(String[] args) throws Exception {
        // Load fingerprint images from files with options for DPI and grayscale conversion
        FingerprintImageOptions options = new FingerprintImageOptions().dpi(500);

        // Load fingerprint images (assuming you have multiple images)
        List<FingerprintTemplate> templates = new ArrayList<>();
        for (int i = 5; i <= 7; i++) {  // Assuming you have 10 fingerprint images
            byte[] imageBytes = Files.readAllBytes(Paths.get("index_" + i + ".png"));
            FingerprintImage image = new FingerprintImage(imageBytes, options);
            templates.add(new FingerprintTemplate(image));
        }

        // Generate genuine and impostor scores
        List<Double> genuineScores = new ArrayList<>();
        List<Double> impostorScores = new ArrayList<>();

        for (int i = 0; i < templates.size(); i++) {
            for (int j = i + 1; j < templates.size(); j++) {
                FingerprintMatcher matcher = new FingerprintMatcher(templates.get(i));
                double score = matcher.match(templates.get(j));
                
                if (i / 2 == j / 2) {  // Assuming every two consecutive images are from the same finger
                    genuineScores.add(score);
                } else {
                    impostorScores.add(score);
                }
            }
        }

        // Calculate FAR and FRR for different thresholds
        List<Double> thresholds = new ArrayList<>();
        List<Double> farRates = new ArrayList<>();
        List<Double> frrRates = new ArrayList<>();

        for (double threshold = 0; threshold <= 100; threshold += 0.1) {
            int falseAccepts = 0;
            int falseRejects = 0;

            for (double score : impostorScores) {
                if (score >= threshold) falseAccepts++;
            }

            for (double score : genuineScores) {
                if (score < threshold) falseRejects++;
            }

            double far = (double) falseAccepts / impostorScores.size();
            double frr = (double) falseRejects / genuineScores.size();

            thresholds.add(threshold);
            farRates.add(far);
            frrRates.add(frr);
        }

        // Create the plot
        XYSeries farSeries = new XYSeries("FAR");
        XYSeries frrSeries = new XYSeries("FRR");

        for (int i = 0; i < thresholds.size(); i++) {
            farSeries.add(thresholds.get(i), farRates.get(i));
            frrSeries.add(thresholds.get(i), frrRates.get(i));
        }

        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(farSeries);
        dataset.addSeries(frrSeries);

        JFreeChart chart = ChartFactory.createXYLineChart(
                "FAR and FRR vs Threshold",
                "Threshold",
                "Rate",
                dataset,
                PlotOrientation.VERTICAL,
                true,
                true,
                false
        );

        XYPlot plot = chart.getXYPlot();
        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer();
        renderer.setSeriesPaint(0, Color.RED);
        renderer.setSeriesPaint(1, Color.BLUE);
        plot.setRenderer(renderer);

        ChartPanel chartPanel = new ChartPanel(chart);
        chartPanel.setPreferredSize(new Dimension(800, 600));

        JFrame frame = new JFrame("FAR/FRR Plot");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setContentPane(chartPanel);
        frame.pack();
        frame.setVisible(true);

        // Print the similarity score and whether the fingerprints match for the original two fingerprints
        byte[] probeImageBytes = Files.readAllBytes(Paths.get("index_bw_3.png"));
        byte[] candidateImageBytes = Files.readAllBytes(Paths.get("index_7.png"));
        FingerprintImage probeImage = new FingerprintImage(probeImageBytes, options);
        FingerprintImage candidateImage = new FingerprintImage(candidateImageBytes, options);
        FingerprintTemplate probe = new FingerprintTemplate(probeImage);
        FingerprintTemplate candidate = new FingerprintTemplate(candidateImage);
        FingerprintMatcher matcher = new FingerprintMatcher(probe);

        double similarity = matcher.match(candidate);
        double threshold = 40;
        boolean matches = similarity >= threshold;

        System.out.println("Similarity score: " + similarity);
        System.out.println("Fingerprint match: " + matches);
    }
}