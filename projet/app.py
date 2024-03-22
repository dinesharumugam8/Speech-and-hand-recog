from flask import Flask, render_template, request
import os
import speech_recognition as sr
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Set the absolute path for the 'uploads' folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the 'uploads' folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

executor = ThreadPoolExecutor(2)

def recognize_stutter_audio(audio_file):
    # Check if file exists
    if not os.path.isfile(audio_file):
        return "Error: Audio file not found."

    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Load audio file
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    try:
        # Recognize speech
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Error: Could not understand the audio."
    except sr.RequestError as e:
        return f"Error: {e}"

def process_audio_file(audio_file):
    return recognize_stutter_audio(audio_file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "Error: No file uploaded."

    file = request.files['file']
    if file.filename == '':
        return "Error: No selected file."

    # Save the uploaded file using an absolute file path
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

    # Get the path to the uploaded file
    audio_file = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

    # Process the uploaded file in a background thread
    future = executor.submit(process_audio_file, audio_file)
    result = future.result()

    return render_template('result.html', result=result)

if __name__ == "__main__":
    app.run(debug=True)