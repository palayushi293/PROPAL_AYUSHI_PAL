from flask import Flask, render_template, request, redirect, url_for
import pickle
import pyttsx3

import whisper
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

model = whisper.load_model("base")
from flask import Flask, render_template, request
from transformers import pipeline

app = Flask(__name__)


generator = pipeline("text-generation", model="gpt2")

@app.route('/generate_quest', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['prompt']
        output = generator(user_input, max_length=100, num_return_sequences=1)
        generated_text = output[0]['generated_text']
        return render_template('result.html', prompt=user_input, result=generated_text)
    return render_template('text_G_Res.html')

if __name__ == "_main_":
    app.run(debug=True)

@app.route('/text', methods=['GET', 'POST'])
def transcribe_audio():
    if request.method == 'POST':
        if 'audio' not in request.files:
            return "No file part", 400

        file = request.files['audio']
        if file.filename == '':
            return "No selected file", 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        file_size = os.path.getsize(filepath)
        print(f"Saved file at: {filepath}, size: {file_size} bytes")

        if file_size == 0:
            os.remove(filepath)
            return "Uploaded file is empty", 400

        try:
            result = model.transcribe(filepath)
            transcription = result['text']
        except Exception as e:
            transcription = f"Transcription failed: {str(e)}"

        os.remove(filepath)
        return render_template('result.html', transcription=transcription)

    return render_template('text.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_text = request.form['text']

       
        with open("speech_text.pkl", "wb") as f:
            pickle.dump(user_text, f)

        
        engine = pyttsx3.init()
        engine.say(user_text)
        engine.runAndWait()

        return redirect(url_for('index'))

    return render_template('index.html')


if __name__ == "_main_":
    app.run(debug=True)