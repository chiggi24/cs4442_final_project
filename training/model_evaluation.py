# Import necessary libraries for model evaluation and visualization
import seaborn as sns  # For creating heatmaps (e.g., confusion matrix)
import matplotlib.pyplot as plt  # For plotting visualizations
from sklearn.preprocessing import label_binarize  # To convert class labels to binary format for ROC/PR curves
import numpy as np  # For numerical operations
import pandas as pd  # For handling and organizing results
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve, auc, precision_recall_curve, classification_report  # Metrics used for evaluating models

# Function to evaluate a single model on a test set with detailed metrics and visualizations
def evaluate_single_model(model, X_test, y_test, class_names):
    """Evaluate a single model with detailed metrics and visualizations."""
    
    # Get the predicted probabilities and convert them to class predictions
    y_pred_probs = model.predict(X_test)
    y_pred = y_pred_probs.argmax(axis=1)

    # Print classification report including precision, recall, f1-score, and support for each class
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names))
    
    # Calculate and print accuracy of the model
    accuracy = np.mean(y_pred == y_test)
    print(f"Accuracy: {accuracy:.2f}")
    
    # Compute confusion matrix and plot it as a heatmap
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()
    
    # Normalize confusion matrix and plot it
    cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    plt.figure(figsize=(6, 6))
    sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Normalized Confusion Matrix')
    plt.show()

    # Binarize the true labels for multiclass ROC AUC calculation
    class_indices = np.arange(len(class_names))
    y_test_bin = label_binarize(y_test, classes=class_indices)

    # Calculate and print ROC AUC score for multiclass classification
    roc_auc = roc_auc_score(y_test_bin, y_pred_probs, average="macro", multi_class="ovr")
    print(f"Multiclass ROC AUC Score: {roc_auc:.2f}")

    # Plot ROC curve for each class and display AUC values
    plt.figure(figsize=(8, 6))
    for i, class_label in enumerate(class_names):
        fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_pred_probs[:, i])
        plt.plot(fpr, tpr, label=f"{class_label} (AUC = {auc(fpr, tpr):.2f})")

    plt.plot([0, 1], [0, 1], color='gray', linestyle='--')  # Diagonal line for random classifier
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve (Multiclass OvR)")
    plt.legend()
    plt.show()
    
    # Plot precision-recall curve for each class and display AUC values
    plt.figure(figsize=(8, 6))
    for i, class_label in enumerate(class_names):
        precision, recall, _ = precision_recall_curve(y_test_bin[:, i], y_pred_probs[:, i])
        plt.plot(recall, precision, label=f"{class_label} (AUC = {auc(recall, precision):.2f})")

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend()
    plt.show()

# Function to compare multiple models and present their performance in a formatted table
def compare_models(trained_models):
    """Compare models and format results similar to the provided table."""
    
    all_results = {}  # Dictionary to store results of each model
    print("Evaluating Models...\n")

    # Loop over each trained model for evaluation
    for model_name, data in trained_models.items():
        y_pred_probs = data["model"].predict(data["X_test"])  # Get predicted probabilities
        y_pred = y_pred_probs.argmax(axis=1)  # Convert probabilities to class predictions
        y_test_bin = label_binarize(data["y_test"], classes=np.arange(len(data["class_names"])))  # Binarize true labels

        per_class_metrics = []  # List to store metrics for each class

        # Loop over each class to calculate precision, recall, and F1-score
        for class_idx in range(len(data["class_names"])):
            class_precision = precision_score(data["y_test"], y_pred, labels=[class_idx], average="macro", zero_division=0)
            class_recall = recall_score(data["y_test"], y_pred, labels=[class_idx], average="macro", zero_division=0)
            class_f1 = f1_score(data["y_test"], y_pred, labels=[class_idx], average="macro", zero_division=0)
            per_class_metrics.append([class_precision, class_recall, class_f1])

        # Create a DataFrame to display per-class metrics
        per_class_df = pd.DataFrame(per_class_metrics, columns=["Precision", "Recall", "F1-score"])

        # Calculate macro-average metrics and accuracy
        accuracy = np.mean(y_pred == data["y_test"])
        macro_precision = precision_score(data["y_test"], y_pred, average="macro")
        macro_recall = recall_score(data["y_test"], y_pred, average="macro")
        macro_f1 = f1_score(data["y_test"], y_pred, average="macro")

        # Add average row to the DataFrame
        per_class_df.loc["Average"] = [macro_precision, macro_recall, macro_f1]
        per_class_df.loc["Accuracy"] = [accuracy, np.nan, np.nan]  # Accuracy is a single value, so it's added once

        # Store the results in the all_results dictionary
        all_results[model_name] = per_class_df

    # Combine the individual model results into one DataFrame
    combined_df = pd.concat(all_results, axis=1)
    
    # Format the combined DataFrame
    combined_df = combined_df.round(2)  # Round metrics to 2 decimal places for clarity
    combined_df.fillna("", inplace=True)  # Remove NaNs to clean up the table
    combined_df.index.name = "CLASS"  # Label the index column as "CLASS"

    # Return the formatted DataFrame with all model comparison results
    return combined_df
