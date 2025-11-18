from flask import Flask, render_template, redirect, request, url_for, flash
from flask_scss import Scss
from modules.add_Domain import addDomain
from modules.read_Domain import readDomain
from modules.update_Domain import updateDomain
from modules.delete_Domain import deleteDomain
from modules.fetch_Domain import fetchDomain
import threading
import os

app = Flask(__name__)
Scss(app)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_secret_key")

# --- Home ---
@app.route("/")
def home():
    return render_template('home.html')

# --- Add Domain ---
@app.route("/add", methods=['GET','POST'])
def add():
    if request.method == 'POST':
        domain = request.form.get('content')
        message = addDomain(domain)
        flash(message)
        return redirect(url_for('add'))
    return render_template('add.html')

# --- Read Domains ---
@app.route("/read")
def read():
    domain = readDomain()
    if not domain:
        flash("No domains in the database",'info')
        return render_template('read.html', data=[])
    return render_template('read.html', data=domain.data)

# --- Update Domain ---
@app.route("/update", methods=['GET','POST'])
def update():
    if request.method == 'POST':
        old = request.form.get('old_content')
        new = request.form.get('new_content')
        message = updateDomain(old, new)
        flash(message)
        return redirect(url_for('update'))
    return render_template('update.html')

# --- Delete Domain ---
@app.route("/delete", methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        domain = request.form.get('del_content')
        message = deleteDomain(domain)
        flash(message)
    return render_template('delete.html')

# --- Fetch Domains (non-blocking) ---
@app.route("/fetch", methods=['GET','POST'])
def fetch():
    if request.method == 'POST':
        # Launch fetchDomain in a separate thread
        thread = threading.Thread(target=fetchDomain)
        thread.daemon = True  # ensures thread exits if server stops
        thread.start()
        flash("Domain verification started in background. You will receive an email when complete.")
        return redirect(url_for('fetch'))
    return render_template('fetch.html')

# --- Main ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False for production

