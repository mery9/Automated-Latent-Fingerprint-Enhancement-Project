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

public class App {
    public static void main(String[] args) throws Exception {
        // Load fingerprint images from files with options for DPI and grayscale conversion
        FingerprintImageOptions options = new FingerprintImageOptions().dpi(500);

        // Load fingerprint images
        byte[] probeImageBytes = Files.readAllBytes(Paths.get("index_bw_1.png"));
        byte[] candidateImageBytes = Files.readAllBytes(Paths.get("index_2.png"));

        FingerprintImage probeImage = new FingerprintImage(probeImageBytes, options);
        FingerprintImage candidateImage = new FingerprintImage(candidateImageBytes, options);

        FingerprintTemplate probe = new FingerprintTemplate(probeImage);
        FingerprintTemplate candidate = new FingerprintTemplate(candidateImage);

        FingerprintMatcher matcher = new FingerprintMatcher(probe);

        // Calculate similarity
        double similarity = matcher.match(candidate);
        double threshold = 18;
        boolean matches = similarity >= threshold;

        // Print the similarity score and whether the fingerprints match
        System.out.println("Similarity score: " + similarity);
        System.out.println("Fingerprint match: " + matches);

        // To generate data for FAR/FRR and ROC curves
        List<Double> falseAcceptRates = new ArrayList<>();
        List<Double> falseRejectRates = new ArrayList<>();
        List<Double> similarityScores = new ArrayList<>();

        // Generate FAR and FRR for different thresholds
        for (int thresholdValue = 0; thresholdValue <= 50; thresholdValue += 1) {
            double score = matcher.match(candidate);
            similarityScores.add(score);

            // Assume we have data to calculate FAR and FRR here (using your dataset)
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

    // Methods to calculate FAR and FRR based on your dataset
    private static double calculateFAR(double threshold, double score) {
        // Implement your logic to calculate FAR based on threshold and score
        // This is a placeholder
        return score >= threshold ? 1.0 : 0.0;
    }

    private static double calculateFRR(double threshold, double score) {
        // Implement your logic to calculate FRR based on threshold and score
        // This is a placeholder
        return score < threshold ? 1.0 : 0.0;
    }

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

    private static void plotFARFRRCurve(List<Double> FARs, List<Double> FRRs) {
        XYSeries farSeries = new XYSeries("FAR Curve");
        XYSeries frrSeries = new XYSeries("FRR Curve");

        for (int i = 0; i < FARs.size(); i++) {
            farSeries.add((Number) i, (Number) FARs.get(i));
            frrSeries.add((Number) i, (Number) FRRs.get(i));
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

    private static void plotROCCurve(List<Double> FARs, List<Double> FRRs) {
        XYSeries series = new XYSeries("ROC Curve");
        for (int i = 0; i < FARs.size(); i++) {
            series.add((Number) FARs.get(i), (Number) (1 - FRRs.get(i)));
        }

        XYSeriesCollection dataset = new XYSeriesCollection(series);
        JFreeChart chart = ChartFactory.createXYLineChart(
            "ROC Curve",
            "False Accept Rate",
            "True Accept Rate",
            dataset,
            PlotOrientation.VERTICAL,
            true,
            true,
            false
        );

        XYPlot plot = chart.getXYPlot();
        XYLineAndShapeRenderer renderer = new XYLineAndShapeRenderer();
        plot.setRenderer(renderer);

        JFrame frame = new JFrame("ROC Curve");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.add(new ChartPanel(chart));
        frame.pack();
        frame.setVisible(true);
    }
}
