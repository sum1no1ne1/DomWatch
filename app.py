from flask import Flask, render_template, redirect, request, url_for, flash
from flask_scss import Scss
from modules.add_Domain import addDomain
from modules.read_Domain import readDomain
from modules.update_Domain import updateDomain
from modules.delete_Domain import deleteDomain
from modules.fetch_Domain import fetchDomain

app=Flask(__name__)
Scss(app)
app.secret_key = "your_secret_key" 

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
        return redirect((url_for('add')))
    return render_template('add.html')

@app.route("/read")
def read():
    domain=readDomain()
    if domain:
        pass
    else:
        flash("no domains in the database",'info')
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
        return redirect((url_for('update')))
    return render_template('update.html')

@app.route("/delete", methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        message=None
        domain=request.form.get('del_content')
        message=deleteDomain(domain)
        flash(message)
        
    return render_template('delete.html')

@app.route("/fetch",methods=['GET','POST'])
def fetch():
    if request.method == 'POST':
        message=None
        message=fetchDomain()
        flash(message)

    return render_template('fetch.html')
if __name__=="__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # use Render's port if available
    app.run(host="0.0.0.0", port=port, debug=True)