import cv2
import numpy as np
from matplotlib import pyplot as plt

# Load the image
image_path = "/home/chai/sourceafis-project/sourceafis-project/Latent/B112L2U.png"
image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Step 1: Denoise the image using Gaussian Blur
denoised = cv2.GaussianBlur(image, (5, 5), 0)

# Step 2: Histogram Equalization for contrast enhancement
equalized = cv2.equalizeHist(denoised)

# Step 3: Apply Adaptive Thresholding for better fingerprint visibility
adaptive_thresh = cv2.adaptiveThreshold(
    equalized, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
)

# Step 4: Use Morphological Transformations to refine edges
kernel = np.ones((2, 2), np.uint8)
morphed = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)

# Step 5: Sharpen the image
sharpening_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
sharpened = cv2.filter2D(morphed, -1, sharpening_kernel)

# Display results
titles = ['Original', 'Denoised', 'Equalized', 'Adaptive Threshold', 'Enhanced']
images = [image, denoised, equalized, adaptive_thresh, sharpened]

plt.figure(figsize=(12, 8))
for i in range(5):
    plt.subplot(2, 3, i+1)
    plt.imshow(images[i], cmap='gray')
    plt.title(titles[i])
    plt.axis('off')

plt.tight_layout()
plt.show()

# Save the enhanced image
output_path = "/mnt/data/enhanced_fingerprint.png"
cv2.imwrite(output_path, sharpened)
print(f"Enhanced fingerprint saved at: {output_path}")
