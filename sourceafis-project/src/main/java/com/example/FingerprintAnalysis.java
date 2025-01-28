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
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class FingerprintAnalysis {
    public static void main(String[] args) throws Exception {
        // Load fingerprint images from files with options for DPI and grayscale conversion
        FingerprintImageOptions options = new FingerprintImageOptions().dpi(500);

        // Load fingerprint images
        byte[] probeImageBytes = Files.readAllBytes(Paths.get("finger_4.png"));
        byte[] candidateImageBytes = Files.readAllBytes(Paths.get("finger_5.png"));

        FingerprintImage probeImage = new FingerprintImage(probeImageBytes, options);
        FingerprintImage candidateImage = new FingerprintImage(candidateImageBytes, options);

        FingerprintTemplate probe = new FingerprintTemplate(probeImage);
        FingerprintTemplate candidate = new FingerprintTemplate(candidateImage);

        FingerprintMatcher matcher = new FingerprintMatcher(probe);

        // Calculate similarity
        double similarity = matcher.match(candidate);
        double threshold = 40;
        boolean matches = similarity >= threshold;

        // Print the similarity score and whether the fingerprints match
        System.out.println("Similarity score: " + similarity);
        System.out.println("Fingerprint match: " + matches);

        // To generate data for FAR/FRR and ROC curves
        List<Double> falseAcceptRates = new ArrayList<>();
        List<Double> falseRejectRates = new ArrayList<>();
        List<Double> similarityScores = new ArrayList<>();

        // Simulate similarity scores to generate FAR and FRR
        for (int thresholdValue = 0; thresholdValue <= 70; thresholdValue += 1) {
            // Simulate a realistic score variation
            double score = matcher.match(candidate) + new Random().nextDouble() * 10;
            similarityScores.add(score);

            // Calculate FAR and FRR using simulated data
            double FAR = calculateFAR(thresholdValue, score);
            double FRR = calculateFRR(thresholdValue, score);

            falseAcceptRates.add(FAR);
            falseRejectRates.add(FRR);
        }

        // Find EER (where FAR and FRR are closest)
        double eer = findEER(falseAcceptRates, falseRejectRates);
        System.out.println("Equal Error Rate (EER): " + eer);

        // Plot FAR and FRR curves
        plotFARFRRCurve(falseAcceptRates, falseRejectRates);

        // Plot ROC Curve
        plotROCCurve(falseAcceptRates, falseRejectRates);
    }

    // Simulate calculation of FAR based on threshold and score
    private static double calculateFAR(double threshold, double score) {
        return score >= threshold ? new Random().nextDouble() * 0.1 : new Random().nextDouble() * 0.9;
    }

    // Simulate calculation of FRR based on threshold and score
    private static double calculateFRR(double threshold, double score) {
        return score < threshold ? new Random().nextDouble() * 0.1 : new Random().nextDouble() * 0.9;
    }

    // Find the Equal Error Rate (EER) by finding the point where FAR and FRR intersect
    private static double findEER(List<Double> FARs, List<Double> FRRs) {
        double eer = 0.0;
        for (int i = 0; i < FARs.size(); i++) {
            if (Math.abs(FARs.get(i) - FRRs.get(i)) < 0.01) {
                eer = FARs.get(i);
                break;
            }
        }
        return eer;
    }

    // Plot FAR and FRR curves using JFreeChart
    private static void plotFARFRRCurve(List<Double> FARs, List<Double> FRRs) {
        XYSeries farSeries = new XYSeries("FAR Curve");
        XYSeries frrSeries = new XYSeries("FRR Curve");

        for (int i = 0; i < FARs.size(); i++) {
            farSeries.add(i, FARs.get(i));
            frrSeries.add(i, FRRs.get(i));
        }

        XYSeriesCollection dataset = new XYSeriesCollection();
        dataset.addSeries(farSeries);
        dataset.addSeries(frrSeries);

        JFreeChart chart = ChartFactory.createXYLineChart(
            "FAR and FRR Curves",
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
        plot.setRenderer(renderer);

        JFrame frame = new JFrame("FAR and FRR Curves");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.add(new ChartPanel(chart));
        frame.pack();
        frame.setVisible(true);
    }

    // Plot ROC curve using FAR and FRR data
    private static void plotROCCurve(List<Double> FARs, List<Double> FRRs) {
        XYSeries series = new XYSeries("ROC Curve");
        for (int i = 0; i < FARs.size(); i++) {
            // Explicitly cast values to Number to avoid ambiguity
            series.add((Number) FARs.get(i), (Number) (1 - FRRs.get(i))); // Flip FRR to get True Acceptance Rate
        }
    
        XYSeriesCollection dataset = new XYSeriesCollection(series);
        JFreeChart chart = ChartFactory.createXYLineChart(
            "ROC Curve",
            "False Acceptance Rate (%)",
            "Genuine Acceptance Rate (%)",
            dataset,
            PlotOrientation.VERTICAL,
            true,
            true,
            false
        );
    
        XYPlot plot = chart.getXYPlot();
        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer(true, false);
        renderer.setSeriesPaint(0, java.awt.Color.GREEN); // Set line color
        renderer.setSeriesStroke(0, new java.awt.BasicStroke(2.0f));
        plot.setRenderer(renderer);
    
        JFrame frame = new JFrame("ROC Curve");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.add(new ChartPanel(chart));
        frame.pack();
        frame.setVisible(true);
    }
}