from flask import Flask, request, render_template, redirect, flash
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = "your_secret_key"  # Replace with a secure key in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # limit file size to 16 MB

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    output = ''
    if request.method == 'POST':
        # Ensure the 'file' part is in the request
        if 'file' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)

        file = request.files['file']

        # Check if the user submitted a file
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        if file:
            # Sanitize the filename and save it to the upload folder
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Call your external Python script (main2.py) passing the file path as an argument
            try:
                # Using subprocess.run to execute main2.py
                result = subprocess.run(
                    ["python", "main2.py", filepath],
                    capture_output=True, text=True, check=True
                )
                output = result.stdout
                print("out", output)
            except subprocess.CalledProcessError as e:
                output = f"An error occurred while processing the file: {e.stderr}"
            if os.path.exists(filepath):
                os.remove(filepath)

    # Render the template with the output result
    return render_template('index.html', output=output)


if __name__ == '__main__':
    app.run(port=4888)
