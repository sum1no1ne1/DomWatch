from flask import Flask, render_template, redirect, request, url_for, flash,session
from flask_scss import Scss
from modules.config import supabase
from modules.add_Domain import addDomain
from modules.read_Domain import readDomain
from modules.update_Domain import updateDomain
from modules.delete_Domain import deleteDomain
from modules.fetch_Domain import fetchDomain
import threading
import os

app = Flask(__name__)
Scss(app)
# app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_secret_key")
app.secret_key = 'your-secret-key-here'

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
        try:
            # Only run domain check when user clicks the button
            fetchDomain()
            flash("Domain verification completed successfully!", 'success')
            # Store a flag in session to indicate processing is complete
            session['processing_complete'] = True
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
        
        return redirect(url_for('fetch'))
    
    # Only show results if processing has been completed in this session
    if session.get('processing_complete'):
        working_result = supabase.table('Domain_table').select('domain_name').eq('is_valid', 'is working').execute()
        working_domains = [d['domain_name'] for d in working_result.data]
        
        not_working_result = supabase.table('Domain_table').select('domain_name', 'verification_reason').eq('is_valid', 'not working').execute()
        not_working_domains = [
            {"domain": d['domain_name'], "reason": d.get('verification_reason', 'Unknown error')}
            for d in not_working_result.data
        ]
        
        results = {
            "working_domains": working_domains,
            "not_working_domains": not_working_domains
        }
    else:
        results = None
    
    return render_template('fetch.html', results=results)
# --- Main ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False for production
    # app.run(debug=True)

