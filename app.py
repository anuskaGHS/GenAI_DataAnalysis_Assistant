from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify, send_file
)
import os
import uuid
import json

# App config
import config

# Core modules
from core.storage import Storage
from core.agent import Agent


# -------------------------------------------------
# APP INITIALIZATION
# -------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["UPLOAD_FOLDER"] = config.UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = config.MAX_FILE_SIZE

storage = Storage()


# -------------------------------------------------
# ROUTE 1: LANDING PAGE
# -------------------------------------------------
@app.route("/")
def get_started():
    return render_template("get_started.html")


# -------------------------------------------------
# ROUTE 2: UPLOAD PAGE
# -------------------------------------------------
@app.route("/upload")
def upload():
    return render_template("upload.html")


# -------------------------------------------------
# ROUTE 3: HANDLE FILE UPLOAD (API)
# -------------------------------------------------
@app.route("/upload_file", methods=["POST"])
def upload_file():
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not storage.allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": "Only CSV and Excel files are allowed"
            }), 400

        session_id = str(uuid.uuid4())
        filepath, filename = storage.save_upload(file, session_id)

        if not filepath:
            return jsonify({"success": False, "error": "File save failed"}), 500

        session["session_id"] = session_id

        return jsonify({
            "success": True,
            "filename": filename,
            "redirect": url_for("overview")
        })

    except Exception as e:
        print(f"Upload error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------------------------------
# ROUTE 4: OVERVIEW PAGE
# -------------------------------------------------
@app.route("/overview")
def overview():
    session_id = session.get("session_id")
    if not session_id:
        return redirect(url_for("upload"))

    session_info = storage.get_session(session_id)
    if not session_info:
        return redirect(url_for("upload"))

    df = storage.load_dataframe(session_info["filepath"])
    if df is None:
        return redirect(url_for("upload"))

    preview = {
        "columns": list(df.columns),
        "rows": df.head(config.PREVIEW_ROWS).to_dict("records"),
        "total_rows": len(df),
        "total_columns": len(df.columns)
    }

    return render_template(
        "overview.html",
        filename=session_info["filename"],
        preview=preview
    )


# -------------------------------------------------
# ROUTE 5: START ANALYSIS (AGENT)
# -------------------------------------------------
@app.route("/start_analysis", methods=["POST"])
def start_analysis():
    try:
        session_id = session.get("session_id")
        if not session_id:
            return jsonify({"success": False, "error": "No active session"}), 400

        agent = Agent(session_id)
        success = agent.run_analysis()

        if success:
            return jsonify({
                "success": True,
                "redirect": url_for("analysis")
            })

        return jsonify({
            "success": False,
            "error": "Analysis failed"
        }), 500

    except Exception as e:
        print(f"Agent error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------------------------------
# ROUTE 6: ANALYSIS PAGE
# -------------------------------------------------
@app.route("/analysis")
def analysis():
    session_id = session.get("session_id")
    if not session_id:
        return redirect(url_for("upload"))

    session_info = storage.get_session(session_id)
    if not session_info or session_info["status"] != "completed":
        return redirect(url_for("overview"))

    profile = json.loads(
        storage.get_analysis_result(session_id, "profile") or "{}"
    )
    charts = json.loads(
        storage.get_analysis_result(session_id, "charts") or "[]"
    )
    insights = storage.get_analysis_result(session_id, "insights")

    return render_template(
        "analysis.html",
        filename=session_info["filename"],
        profile=profile,
        charts=charts,
        insights=insights
    )


# -------------------------------------------------
# ROUTE 7: FINAL REPORT PAGE
# -------------------------------------------------
@app.route("/report")
def report():
    session_id = session.get("session_id")
    if not session_id:
        return redirect(url_for("upload"))

    session_info = storage.get_session(session_id)
    if not session_info or session_info["status"] != "completed":
        return redirect(url_for("overview"))

    report_data = json.loads(
        storage.get_analysis_result(session_id, "report") or "{}"
    )

    return render_template(
        "report.html",
        filename=session_info["filename"],
        report=report_data
    )


# -------------------------------------------------
# ROUTE 8: SERVE CHART IMAGES
# -------------------------------------------------
@app.route("/charts/<session_id>/<filename>")
def serve_chart(session_id, filename):
    chart_path = os.path.join(
        config.UPLOAD_FOLDER, "charts", session_id, filename
    )

    if os.path.exists(chart_path):
        return send_file(chart_path, mimetype="image/png")

    return "Chart not found", 404


# -------------------------------------------------
# ROUTE 9: RESET SESSION
# -------------------------------------------------
@app.route("/new_analysis")
def new_analysis():
    session.clear()
    return redirect(url_for("get_started"))


# -------------------------------------------------
# ERROR HANDLERS
# -------------------------------------------------
@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "error": f"File too large (max {config.MAX_FILE_SIZE // (1024*1024)} MB)"
    }), 413


@app.errorhandler(404)
def not_found(error):
    return redirect(url_for("get_started"))


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Internal server error"}), 500


# -------------------------------------------------
# RUN APP
# -------------------------------------------------
if __name__ == "__main__":
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=config.DEBUG, host="0.0.0.0", port=5000)
