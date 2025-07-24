from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

data_file = 'data.json'

def load_data():
    print("Loading data from file...")
    if not os.path.exists(data_file):
        print("Data file not found, returning empty dict.")
        return {}
    with open(data_file, 'r') as f:
        try:
            data = json.load(f)
            print("Data loaded successfully:", data)
            return data
        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
            return {}

def save_data(data):
    print("Saving data to file:", data)
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=2)
    print("Data saved successfully.")

@app.route('/')
def index():
    print("Handling request to '/' route")
    records = load_data()
    totals = {person: sum(item['severity'] for item in infractions) for person, infractions in records.items()}
    print("Totals calculated:", totals)
    return render_template('index.html', records=records, totals=totals, people=records.keys())

@app.route('/add', methods=['POST'])
def add_infraction():
    print("Handling '/add' POST request")
    records = load_data()

    selected_person = request.form['person']
    new_person = request.form.get('new_person', '').strip()

    print(f"Selected person: {selected_person}, New person input: {new_person}")

    person = new_person if selected_person == '__new__' and new_person else selected_person
    if not person:
        print("Error: No person provided.")
        return jsonify({'error': 'No person provided'}), 400

    severity = int(request.form['severity'])
    date = request.form['date']
    print(f"Adding infraction: person={person}, severity={severity}, date={date}")

    if person not in records:
        print(f"Person {person} not in records. Creating new entry.")
        records[person] = []

    records[person].append({
        'severity': severity,
        'date': date
    })

    save_data(records)

    total = sum(item['severity'] for item in records[person])
    print(f"New total severity for {person}: {total}")
    return jsonify({'person': person, 'new_total': total})

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
