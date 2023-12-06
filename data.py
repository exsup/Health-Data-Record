from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health_data.db'
db = SQLAlchemy(app)

class HealthEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    dob = db.Column(db.Date, nullable=False)
    flu_shot = db.Column(db.String(3), nullable=False)
    covid_vaccine = db.Column(db.String(3), nullable=False)
    phone_number = db.Column(db.String(15))

    def __repr__(self):
        return f'<HealthEntry {self.id}>'

# Create tables before the first request
@app.before_request
def before_request():
    if request.endpoint != 'static':  # Exclude static files from creating tables
        db.create_all()

@app.route('/')
def index():
    entries = HealthEntry.query.order_by(HealthEntry.dob.desc()).all()
    return render_template('index.html', entries=entries)

@app.route('/add_entry', methods=['POST'])
def add_entry():
    if request.method == 'POST':
        last_name = request.form.get('lastName')
        middle_name = request.form.get('middleName')
        dob = request.form.get('dob')
        flu_shot = request.form.get('fluShot')
        covid_vaccine = request.form.get('covidVaccine')
        phone_number = request.form.get('phoneNumber')

        new_entry = HealthEntry(
            last_name=last_name,
            middle_name=middle_name,
            dob=datetime.strptime(dob, '%Y-%m-%d'),
            flu_shot=flu_shot,
            covid_vaccine=covid_vaccine,
            phone_number=phone_number
        )

        db.session.add(new_entry)
        db.session.commit()

        # Redirect to the view_entries route
        return redirect(url_for('view_entries'))

@app.route('/view_entries')
def view_entries():
    # Retrieve all entries from the database
    entries = HealthEntry.query.all()
    return render_template('view_entries.html', entries=entries)



@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    entry_to_delete = HealthEntry.query.get_or_404(entry_id)
    
    # Delete the entry from the database
    db.session.delete(entry_to_delete)
    db.session.commit()

    # Redirect to the view_entries route
    return redirect(url_for('view_entries'))

@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry_to_edit = HealthEntry.query.get_or_404(entry_id)

    if request.method == 'POST':
        entry_to_edit.last_name = request.form.get('lastName')
        entry_to_edit.middle_name = request.form.get('middleName')
        entry_to_edit.dob = datetime.strptime(request.form.get('dob'), '%Y-%m-%d')
        entry_to_edit.flu_shot = request.form.get('fluShot')
        entry_to_edit.covid_vaccine = request.form.get('covidVaccine')
        entry_to_edit.phone_number = request.form.get('phoneNumber')

        db.session.commit()

        # Redirect to the view_entries route
        return redirect(url_for('view_entries'))
    
    # Render the edit form
    return render_template('edit_entry.html', entry=entry_to_edit)

if __name__ == '__main__':
    app.run(debug=True)