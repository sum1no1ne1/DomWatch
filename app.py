from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_scss import Scss
from modules.add_Domain import addDomain
from modules.read_Domain import readDomain
from modules.update_Domain import updateDomain
from modules.delete_Domain import deleteDomain
from modules.fetch_Domain import fetchDomain
import threading
import logging
import os
import time

# --- logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# --- Flask app setup ---
app = Flask(__name__)
Scss(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_secret_key")

# Optional small status file for checking job status
STATUS_FILE = "fetch_status.txt"

def set_status(text: str):
    """Write a short status message (timestamped) to a file (optional)."""
    try:
        with open(STATUS_FILE, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")
    except Exception as e:
        logger.warning("Could not write status file: %s", e)

def background_fetch_job():
    """Wrapper that runs the heavy fetchDomain() job and logs errors.
       This runs in a daemon thread so it won't block Gunicorn worker.
    """
    logger.info("Background fetch job started.")
    set_status("Started fetch job")
    try:
        result = fetchDomain()  # your existing function which does checks/screenshots/pdf/email
        # fetchDomain returns a message string — log it
        logger.info("Background fetch job finished: %s", result)
        set_status(f"Finished fetch job: {result}")
    except Exception as e:
        logger.exception("Background fetch job raised an exception: %s", e)
        set_status(f"Fetch job error: {e}")

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/add", methods=['GET','POST'])
def add():
    message=None
    if request.method == 'POST':
        domain = request.form.get('content')
        message = addDomain(domain)
        flash(message)
        return redirect(url_for('add'))
    return render_template('add.html')

@app.route("/read")
def read():
    domain=readDomain()
    if not domain:
        flash("No domains in the database",'info')
        return render_template('read.html', data=[])
    data=domain.data
    return render_template('read.html',data=data)

@app.route("/update", methods=['GET','POST'])
def update():
    message=None
    if request.method == 'POST':
        old=request.form.get('old_content')
        new=request.form.get('new_content')
        message=updateDomain(old,new)
        flash(message)
        return redirect(url_for('update'))
    return render_template('update.html')

@app.route("/delete", methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        domain=request.form.get('del_content')
        message=deleteDomain(domain)
        flash(message)
    return render_template('delete.html')

# --- Fetch route (non-blocking) ---
@app.route("/fetch", methods=['GET','POST'])
def fetch():
    if request.method == 'POST':
        # Check if a job appears to be running (naive check via status file last line)
        try:
            if os.path.exists(STATUS_FILE):
                with open(STATUS_FILE, "r") as f:
                    last_lines = f.readlines()[-1:]  # last line
                if last_lines:
                    last = last_lines[0].lower()
                    # basic heuristic: if last status was "started" less than X minutes ago,
                    # avoid launching duplicate jobs. Adjust X if needed.
                    if "started fetch job" in last or "started fetch job" in last.lower():
                        flash("A fetch job recently started — new job launched anyway.")
            # Launch the background job
            thread = threading.Thread(target=background_fetch_job)
            thread.daemon = True
            thread.start()
            flash("Domain verification started in background. You will receive an email when complete.")
            logger.info("Launched background fetch thread (PID thread: %s)", thread.ident)
            return redirect(url_for('fetch'))
        except Exception as e:
            logger.exception("Failed to start background fetch thread: %s", e)
            flash(f"Failed to start fetch job: {e}", "error")
            return redirect(url_for('fetch'))

    # GET -> show fetch page
    return render_template('fetch.html')

# Optional: small endpoint to check last statuses (machine-readable)
@app.route("/fetch_status")
def fetch_status():
    if not os.path.exists(STATUS_FILE):
        return jsonify({"status": "no history"}), 200
    try:
        with open(STATUS_FILE, "r") as f:
            lines = f.readlines()[-10:]  # last 10 entries
        return jsonify({"status_lines": [l.strip() for l in lines]}), 200
    except Exception as e:
        logger.exception("Error reading status file: %s", e)
        return jsonify({"error": str(e)}), 500

if __name__=="__main__":
    port = int(os.environ.get("PORT", 5000))
    # In production (Render) gunicorn will be used; debug False to match behavior.
    app.run(host="0.0.0.0", port=port, debug=False)
