from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

heading = ('Amount', 'Date', 'Reason')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expense.db'
db = SQLAlchemy(app)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    date = db.Column(db.Integer)
    #date = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.id

@app.route("/", methods=['POST', 'GET'])
def home():
    return render_template("home.html")




@app.route('/fail', methods=['POST', 'GET'])
def fail():
    amount = request.form.get('amount')
    date = request.form.get('date')
    reason = request.form.get('reason')

    if not amount or not date or not reason:
        error_statement = "All fields are required..."
        return render_template('records.html', error_statement=error_statement, amount=amount, date=date, reason=reason)



@app.route('/records', methods=['POST', 'GET'])
def records():
    title = "my expenses!"
    heading = ('Amount', 'Date', 'Reason')


    if request.method == 'POST':
        user = Budget(amount = request.form['amount'], date = request.form['date'], reason = request.form['reason'])

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/records')
        except:
            return "There was an error adding your new record into database"



    else:
        expense = Budget.query.order_by(Budget.date)
        return render_template("records.html", title=title, expense=expense, heading=heading)


@app.route('/update/<int:id>', methods=['POST', 'GET'])
def update(id):
    record_to_update = Budget.query.get_or_404(id)
    if request.method == "POST":
        record_to_update.amount = request.form['amount']
        record_to_update.date = request.form['date']
        record_to_update.reason = request.form['reason']

        try:
            db.session.commit()
            return redirect("/records")
        except:
            return "there was an error updating your record"
    else:
        return render_template('update.html', record_to_update=record_to_update)

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    record_to_delete = Budget.query.get_or_404(id)

    try:
        db.session.delete(record_to_delete)
        db.session.commit()
        return redirect('/records')
    except:
        return "The record could not be deleted"

@app.route('/analysis', methods=['POST', 'GET'])
def analysis():
    conn = sqlite3.connect("expense.db")
    df = pd.read_sql_query("SELECT * FROM Budget", conn)
    db = df.amount.sum()
    df.date = pd.to_datetime(df.date)
    x = 0
    num = 0
    if request.method == 'POST':
        x = request.form['month']


    db2 = df[df.date.dt.month == int(x)].amount.sum()
    return render_template('analysis.html', db=db, x=x, db2=db2)



@app.route('/data')
def data():
    conn = sqlite3.connect("expense.db")
    df = pd.read_sql_query("SELECT * FROM Budget", conn)
    return df.to_html()
