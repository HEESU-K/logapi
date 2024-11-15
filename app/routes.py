from flask import Blueprint, request, jsonify
from app.services import log_message, filter_logs, analyze_log_frequency, analyze_error_ratio
from app.utils import send_error_alert
from functools import wraps
from config import Config

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/logs', methods=['POST'])
def log():
    data = request.json
    log_message(data["level"], data["message"], data.get("source", "default"))
    return jsonify({"status": "Log saved"}), 201

@api_blueprint.route('/logs/filter', methods=['GET'])
def logs_filter():
    level = request.args.get('level')
    keyword = request.args.get('keyword')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    filtered_logs = filter_logs(level, keyword, start_date, end_date)
    return jsonify(filtered_logs)

@api_blueprint.route('/logs/stats', methods=['GET'])
def logs_stats():
    freq_data = analyze_log_frequency()
    error_data = analyze_error_ratio()
    return jsonify({"frequency": freq_data, "error_ratio": error_data})

