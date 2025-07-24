from flask import Flask, render_template, request, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'infractions.json'

# Load or initialize data
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    records = load_data()
    totals = {
        person: sum(item['severity'] for item in infractions)
        for person, infractions in records.items()
    }
    return render_template('index.html', records=records, totals=totals)

@app.route('/add', methods=['POST'])
def add_infraction():
    data = load_data()
    person = request.form['person'].strip()
    description = request.form['description'].strip()
    severity = int(request.form['severity'])

    if person not in data:
        data[person] = []

    data[person].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "severity": severity,
        "description": description
    })

    save_data(data)
    return redirect('/')

@app.route('/api/people')
def api_people():
    data = load_data()
    return jsonify(list(data.keys()))

if __name__ == '__main__':
    app.run(debug=True)