from flask import Flask, render_template, request, jsonify
import pyaudio
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import threading
import time

app = Flask(__name__)

# Konfigurasi perekaman suara
chunk = 1024  # Jumlah sampel per frame
format = pyaudio.paInt16
channels = 1
sample_rate = 44100  # Tingkat sampel (sampel per detik)

# Inisialisasi PyAudio
p = pyaudio.PyAudio()

# Variabel global untuk menyimpan data suara yang direkam
recorded_data = []

# Fungsi untuk merekam suara
def record_sound():
    global recorded_data
    frames = []

    # Membuat objek untuk merekam audio
    stream = p.open(format=format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    # Merekam audio sampai tombol stop ditekan
    while True:
        data = stream.read(chunk)
        frames.append(data)
        if not recording:  # Jika perekaman dihentikan
            break

    # Menghentikan dan menutup stream
    stream.stop_stream()
    stream.close()

    # Menggabungkan dan mengonversi data ke dalam bentuk array numpy
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    recorded_data = audio_data.tolist()

# Fungsi untuk membuat plot
def create_plot(x, y):
    fig = make_subplots(rows=1, cols=1)
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Sound'), row=1, col=1)
    fig.update_layout(title='Sound Waveform')
    return fig

# Variabel global untuk menentukan status perekaman
recording = False

@app.route('/', methods=['GET', 'POST'])
def index():
    global recording
    if request.method == 'POST':
        if not recording:
            # Start recording in a separate thread
            recording = True
            threading.Thread(target=record_sound).start()
            return "Recording..."
        else:
            # Stop recording
            recording = False
            return "Stop recording..."

    # Render initial page with empty plot
    fig = create_plot([], [])
    return render_template('index.html', plot=fig.to_html(full_html=False))

@app.route('/data')
def get_data():
    global recorded_data
    return jsonify({'data': recorded_data})

if __name__ == '__main__':
    app.run(debug=True)
