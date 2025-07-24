from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__)

data_file = 'data.json'

def load_data():
    if not os.path.exists(data_file):
        return {}
    with open(data_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    records = load_data()
    totals = {person: sum(item['severity'] for item in infractions) for person, infractions in records.items()}
    return render_template('index.html', records=records, totals=totals, people=records.keys())

@app.route('/add', methods=['POST'])
def add_infraction():
    records = load_data()

    selected_person = request.form['person']
    new_person = request.form.get('new_person', '').strip()

    person = new_person if selected_person == '__new__' and new_person else selected_person
    if not person:
        return "No person provided", 400

    severity = int(request.form['severity'])
    date = request.form['date']

    if person not in records:
        records[person] = []

    records[person].append({
        'severity': severity,
        'date': date
    })

    save_data(records)

    # ✅ Redirect back to homepage
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
