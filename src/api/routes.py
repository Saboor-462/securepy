from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
from ..utils.dp import dp_count, dp_sum

api_bp = Blueprint("api", __name__)

SAMPLE_DATA = [5, 7, 3, 9, 2, 10, 4]  

@api_bp.get("/health")
def health():
    return jsonify(status="ok")

@api_bp.get("/privacy/count")
@jwt_required()
def privacy_count():
    eps = current_app.config.get("DP_EPSILON", 1.0)
    noisy = dp_count(SAMPLE_DATA, eps)
    return jsonify({"epsilon": eps, "noisy_count": noisy})

@api_bp.get("/privacy/sum")
@jwt_required()
def privacy_sum():
    eps = current_app.config.get("DP_EPSILON", 1.0)
    noisy = dp_sum(SAMPLE_DATA, eps, sensitivity=10.0)
    return jsonify({"epsilon": eps, "noisy_sum": noisy})