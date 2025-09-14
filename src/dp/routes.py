import pandas as pd
from flask import Blueprint, request, jsonify
from diffprivlib.mechanisms import Laplace, Gaussian, Exponential

dp_bp = Blueprint("dp", __name__)

@dp_bp.route("/analyze", methods=["POST"])
def analyze_dataset():
    file = request.files.get("file")
    epsilon = float(request.form.get("epsilon", 1.0))
    delta = float(request.form.get("delta", 1e-5))
    column_name = request.form.get("column_name")
    operation = request.form.get("operation", "mean")
    mechanism_type = request.form.get("mechanism", "laplace")

    if not file or not column_name:
        return jsonify({"error": "File or column not specified"}), 400

    df = pd.read_csv(file)

    if column_name not in df.columns:
        return jsonify({"error": f"Column '{column_name}' not found"}), 400

    if not pd.api.types.is_numeric_dtype(df[column_name]):
        return jsonify({"error": f"Column '{column_name}' is not numeric"}), 400

    col_data = df[column_name].dropna()
    sensitivity = (col_data.max() - col_data.min()) or 1

    # Initialize mechanism
    if mechanism_type == "laplace":
        mech = Laplace(epsilon=epsilon, sensitivity=sensitivity)
    elif mechanism_type == "gaussian":
        mech = Gaussian(epsilon=epsilon, delta=delta, sensitivity=sensitivity)
    elif mechanism_type == "exponential":
        mech = Exponential(epsilon=epsilon, sensitivity=sensitivity)
    else:
        return jsonify({"error": f"Unknown mechanism '{mechanism_type}'"}), 400

    result = {
        "column": column_name,
        "epsilon": epsilon,
        "operation": operation,
        "mechanism": mechanism_type
    }

    if operation == "mean":
        true_val = col_data.mean()
        dp_val = mech.randomise(true_val)
    elif operation == "sum":
        true_val = col_data.sum()
        dp_val = mech.randomise(true_val)
    elif operation == "count":
        true_val = len(col_data)
        dp_val = mech.randomise(true_val)
    elif operation == "histogram":
        true_val = col_data.value_counts().to_dict()
        dp_val = {k: mech.randomise(v) for k, v in true_val.items()}
    elif operation == "full_column":
        true_val = col_data.tolist()
        dp_val = [mech.randomise(v) for v in col_data]
    else:
        return jsonify({"error": f"Unsupported operation '{operation}'"}), 400

    result["true_value"] = true_val
    result["dp_value"] = dp_val

    return jsonify(result)
