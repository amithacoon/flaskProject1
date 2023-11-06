import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
app = Flask(__name__)
UPLOAD_FOLDER = 'static/updates'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'wav'}  # Set of allowed file extensions
# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
results = {}



@app.route('/')
def index():
    # Assume you have an 'index.html' template that represents the homepage
    # with your sidebar and content area as described in your HTML.
    # You can pass necessary data to render your homepage as needed.
    return render_template('index.html')



# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route for the file upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get the duration of the WAV file
            duration = get_wav_duration(filepath)

            # Append the file name and duration to the 'results_db.txt' file
            with open('results_db.txt', 'a') as db:
                db.write(f"{filename},{duration}\n")  # Write the filename and duration separated by a comma

            # Redirect to the score table with the filename
            return redirect(url_for('score'))
    # If it's a GET request or if no file has been uploaded, render the upload page
    return render_template('index.html', message="File upload failed.", status="error")



@app.route('/score')
def score():
    # Initialize an empty list to store file information
    files_info = []

    # Your database file where filenames and durations are stored
    db_file_path = 'results_db.txt'

    # Check if the 'results_db.txt' file exists, create if it does not
    if not os.path.exists(db_file_path):
        with open(db_file_path, 'w'):  # This will create the file if it does not exist
            pass

    # Read the 'results_db.txt' file to get the list of file information
    with open(db_file_path, 'r') as db:
        for line in db:
            name, duration = line.strip().split(',')  # Assuming each line is in the format 'filename,duration'
            files_info.append({'name': name, 'duration': duration})

    # Pass the list of file information to the template
    return render_template('index.html', files_info=files_info, message="File uploaded successfully!", status="success")



import contextlib
import wave


def get_wav_duration(filename):
    with contextlib.closing(wave.open(filename, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration_seconds = frames / float(rate)

        # Convert to hours, minutes, and seconds
        hours = int(duration_seconds // 3600)  # Get the whole hours
        minutes = int((duration_seconds % 3600) // 60)  # Get the remaining minutes
        seconds = int(duration_seconds % 60)  # Get the remaining seconds

        # Format the duration string based on the length
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


# Example usage:
# duration_str = get_wav_duration("path_to_your_file.wav")
# print(duration_str)


if __name__ == "__main__":
    app.run(debug=True)