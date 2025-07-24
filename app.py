from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
import openpyxl
import json
import os
from io import BytesIO


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
    notes = request.form.get('notes', '').strip()  # ✅ Get notes

    if person not in records:
        records[person] = []

    records[person].append({
        'severity': severity,
        'date': date,
        'notes': notes  # ✅ Save notes
    })

    save_data(records)
    return redirect(url_for('index'))

@app.route('/export')
def export_excel():
    records = load_data()

    # Create a workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Infractions'

    # Header row
    ws.append(['Person', 'Date', 'Severity', 'Notes'])

    # Fill data
    for person, infractions in records.items():
        for entry in infractions:
            ws.append([
                person,
                entry.get('date', ''),
                entry.get('severity', ''),
                entry.get('notes', '')
            ])

    # Save to memory buffer
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        download_name='infractions.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
if __name__ == '__main__':
    app.run(debug=True)
