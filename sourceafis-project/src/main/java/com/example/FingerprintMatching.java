package com.example;

import com.machinezoo.sourceafis.FingerprintMatcher;
import com.machinezoo.sourceafis.FingerprintTemplate;
import com.machinezoo.sourceafis.FingerprintImage;
import com.machinezoo.sourceafis.FingerprintImageOptions;

import java.nio.file.Files;
import java.nio.file.Paths;

public class FingerprintMatching {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java FingerprintMatching <path_to_fingerprint1> <path_to_fingerprint2>");
            return;
        }

        try {
            // Load the first fingerprint image and create a template
            FingerprintTemplate fingerprint1 = new FingerprintTemplate(
                new FingerprintImage(
                    Files.readAllBytes(Paths.get(args[0])),
                    new FingerprintImageOptions().dpi(500)
                )
            );

            // Load the second fingerprint image and create a template
            FingerprintTemplate fingerprint2 = new FingerprintTemplate(
                new FingerprintImage(
                    Files.readAllBytes(Paths.get(args[1])),
                    new FingerprintImageOptions().dpi(500)
                )
            );

            // Match the templates
            FingerprintMatcher matcher = new FingerprintMatcher(fingerprint1);
            double score = matcher.match(fingerprint2);

            // Output the similarity score
            System.out.println("Similarity score: " + score);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
