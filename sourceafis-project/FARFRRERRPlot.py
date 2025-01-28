import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score

# Load scores from the CSV file
data = pd.read_csv('scores.csv')

# Separate genuine and impostor scores
genuine_scores = data[data['Label'] == 'genuine']['Score'].values
impostor_scores = data[data['Label'] == 'impostor']['Score'].values

# Check if the scores are not empty to avoid division by zero
if len(genuine_scores) == 0 or len(impostor_scores) == 0:
    print("Error: Genuine or impostor scores are empty, please check your data.")
    exit()

# Compute thresholds for FAR and FRR
thresholds = np.linspace(min(data['Score']), max(data['Score']), 100)
far = []
frr = []

# Calculate FAR and FRR for each threshold
for threshold in thresholds:
    far_value = np.sum(impostor_scores >= threshold) / len(impostor_scores) if len(impostor_scores) > 0 else np.nan
    frr_value = np.sum(genuine_scores < threshold) / len(genuine_scores) if len(genuine_scores) > 0 else np.nan
    far.append(far_value)
    frr.append(frr_value)

# Convert lists to numpy arrays for numerical operations
far = np.array(far)
frr = np.array(frr)

# Remove NaN values to avoid issues when calculating EER
valid_indices = ~np.isnan(far) & ~np.isnan(frr)
far = far[valid_indices]
frr = frr[valid_indices]
thresholds = thresholds[valid_indices]

# Check if there are any valid values left for EER calculation
if len(far) == 0 or len(frr) == 0:
    print("Error: No valid FAR and FRR values available for EER calculation.")
    exit()

# Find EER (Equal Error Rate)
eer_threshold = thresholds[np.nanargmin(np.abs(far - frr))]
eer = far[np.nanargmin(np.abs(far - frr))]

# Ensure FAR is non-increasing
far = np.maximum.accumulate(far[::-1])[::-1]  # Forces FAR to be decreasing by making it non-increasing

# Plot FAR, FRR, and EER
plt.figure(figsize=(10, 6))
plt.plot(thresholds, far, label='FAR (False Acceptance Rate)', linewidth=3)
plt.plot(thresholds, frr, label='FRR (False Rejection Rate)', linewidth=3)
plt.axvline(eer_threshold, linestyle='--', color='red', label=f'EER: {eer:.2f} at threshold {eer_threshold:.2f}')
plt.xlabel('Threshold')
plt.ylabel('Rate')
plt.title('FAR, FRR, and EER Curve')
plt.legend()
plt.grid(True)
plt.show()

# Compute ROC curve
scores = np.concatenate([genuine_scores, impostor_scores])
labels = np.concatenate([np.ones(len(genuine_scores)), np.zeros(len(impostor_scores))])
fpr, tpr, _ = roc_curve(labels, scores)
roc_auc = roc_auc_score(labels, scores)

# Plot ROC Curve
plt.figure(figsize=(10, 6))
plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.grid(True)
plt.show()
