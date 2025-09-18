
from flask import Blueprint, request, jsonify, send_file, url_for, current_app, make_response
import pandas as pd
import numpy as np
import os, uuid, math, random
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

dp_bp = Blueprint("dp", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # backend/
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
PLOT_FOLDER = os.path.join(BASE_DIR, "plots")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)

#Utility DP mechanisms
def laplace_mechanism_scalar(value, epsilon, sensitivity=1.0):
    scale = sensitivity / max(epsilon, 1e-12)
    noise = np.random.laplace(0.0, scale)
    try:
        return float(value) + noise
    except Exception:
        return value

def gaussian_mechanism_scalar(value, epsilon, delta, sensitivity=1.0):
    # Approximate sigma according to standard DP bound
    if delta <= 0:
        delta = 1e-12
    sigma = math.sqrt(2 * math.log(1.25 / delta)) * (sensitivity / max(epsilon, 1e-12))
    noise = np.random.normal(0.0, sigma)
    try:
        return float(value) + noise
    except Exception:
        return value

def exponential_mechanism_categorical(value, epsilon, categories):
    # Simple randomized response style exponential mechanism (not exact formal score)
    # Bias to keep original with higher prob
    if not categories:
        return value
    if random.random() < 0.7:
        return value
    else:
        return random.choice(categories)

#apply noise to column values
def privatize_column_series(series, mechanism, epsilon, delta):
    """Return new series with per-value noise applied according to mechanism."""
    if pd.api.types.is_numeric_dtype(series):
        if mechanism == "laplace":
            return series.apply(lambda x: laplace_mechanism_scalar(x, epsilon))
        elif mechanism == "gaussian":
            return series.apply(lambda x: gaussian_mechanism_scalar(x, epsilon, delta))
        else:
            # exponential on numeric -> fallback to laplace
            return series.apply(lambda x: laplace_mechanism_scalar(x, epsilon))
    else:
        categories = series.dropna().unique().tolist()
        if mechanism == "exponential":
            return series.apply(lambda x: exponential_mechanism_categorical(x, epsilon, categories))
        else:
            # for non-numeric with laplace/gaussian, just keep original or randomize slightly
            return series.apply(lambda x: exponential_mechanism_categorical(x, epsilon, categories))

# Helper: plot comparison histogram
def make_hist_plot(orig_series, priv_series, file_id, column_name):
    # numeric only: hist of original vs privatized
    plot_path = os.path.join(PLOT_FOLDER, f"{file_id}_{column_name}.png")
    plt.figure(figsize=(6,4))
    try:
        if pd.api.types.is_numeric_dtype(orig_series):
            plt.hist(orig_series.dropna().astype(float), bins=30, alpha=0.5, label='original')
            plt.hist(pd.to_numeric(priv_series.dropna(), errors='coerce').dropna(), bins=30, alpha=0.5, label='privatized')
            plt.legend()
            plt.title(f"{column_name}: original vs privatized")
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()
            return plot_path
        else:
            # For categorical, show bar charts of top categories
            orig_counts = orig_series.fillna("NULL").value_counts().nlargest(10)
            priv_counts = priv_series.fillna("NULL").value_counts().reindex(orig_counts.index, fill_value=0)
            df = pd.DataFrame({"original": orig_counts, "privatized": priv_counts})
            df.plot(kind='bar', figsize=(8,4))
            plt.title(f"{column_name}: original vs privatized (top categories)")
            plt.tight_layout()
            plt.savefig(plot_path)
            plt.close()
            return plot_path
    except Exception as e:
        plt.close()
        return None

# Main analyze route
@dp_bp.route("/analyze", methods=["POST"])
def analyze():
    
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    mechanism = request.form.get("mechanism", "laplace")
    epsilon = float(request.form.get("epsilon", 1.0))
    delta = float(request.form.get("delta", 1e-5))
    scope = request.form.get("scope", "single_column")  
    columns = request.form.getlist("columns")  

    file_id = str(uuid.uuid4())
    uploaded_filename = f"{file_id}_input.csv"
    input_path = os.path.join(UPLOAD_FOLDER, uploaded_filename)
    file.save(input_path)

    #load
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        return jsonify({"error": f"Failed to read CSV: {e}"}), 400

    #Decide which columns to process
    if scope == "whole_file":
        cols_to_priv = df.columns.tolist()
    else:
        if not columns:
            #if none chosen, default to first numeric column
            cols_to_priv = [df.columns[0]] if len(df.columns) > 0 else []
        else:
            cols_to_priv = columns

    cols_processed = []
    plot_urls = {}

    privatized_df = df.copy()

    for col in cols_to_priv:
        if col not in df.columns:
            continue
        orig_series = df[col]
        #apply row-level per-value noise
        new_series = privatize_column_series(orig_series, mechanism, epsilon, delta)
        privatized_df[col] = new_series
        cols_processed.append(col)
        #create plot for this column (if possible)
        plot_path = make_hist_plot(orig_series, new_series, file_id, col)
        if plot_path:
            #serve via /dp/plot/<file_id>/<col>
            plot_urls[col] = request.host_url[:-1] + url_for("dp.plot_image", file_id=file_id, column_name=col)

        else:
            plot_urls[col] = None

    #Save privatized CSV
    output_name = f"privatized_{file_id}.csv"
    output_path = os.path.join(OUTPUT_FOLDER, output_name)
    privatized_df.to_csv(output_path, index=False)

    #Return response with download URL and plot map
    download_url = url_for("dp.download", file_id=file_id)
    return jsonify({
        "file_id": file_id,
        "privatized_csv_url": download_url,
        "plots": plot_urls,
        "columns_processed": cols_processed
    }), 200


#Download endpoint
@dp_bp.route("/download/<file_id>", methods=["GET"])
def download(file_id):
    filename = f"privatized_{file_id}.csv"
    path = os.path.join(OUTPUT_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
    return send_file(path, as_attachment=True, download_name="privatized.csv")

#Plot image endpoint
@dp_bp.route("/plot/<file_id>/<column_name>", methods=["GET"])
def plot_image(file_id, column_name):
    plot_path = os.path.join(PLOT_FOLDER, f"{file_id}_{column_name}.png")
    if not os.path.exists(plot_path):
        return jsonify({"error": "Plot not available"}), 404
    # return image file
    return send_file(plot_path, mimetype="image/png")

