import os
import streamlit as st
from yt_dlp import YoutubeDL
import ffmpeg  # Importa ffmpeg-python

# Directory per salvare i file audio
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Funzione per scaricare e convertire l'audio
def download_and_convert_to_wav(url, sampling_rate):
    """Scarica il video da YouTube e salva l'audio in formato WAV con il sampling rate scelto."""
    try:
        # Opzioni per yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',  # Scarica il miglior audio disponibile
            'outtmpl': os.path.join(OUTPUT_DIR, '%(title)s.%(ext)s'),  # Nome del file
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '0',  # Usa la qualità originale
            }],
            'postprocessor_args': ['-ar', str(sampling_rate)],  # Imposta sampling rate
        }

        # Scarica il file audio
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'audio')

        # Rinomina il file scaricato in WAV
        input_file = os.path.join(OUTPUT_DIR, f"{title}.wav")
        output_file = os.path.join(OUTPUT_DIR, f"{title}_converted.wav")

        # Usa ffmpeg-python per convertire il file
        try:
            ffmpeg.input(input_file).output(output_file, ar=sampling_rate).run(overwrite_output=True)
        except Exception as e:
            st.error(f"Errore durante la conversione con FFmpeg: {e}")
            return None

        return f"{title}_converted.wav"

    except Exception as e:
        st.error(f"Errore durante la conversione: {e}")
        return None

# Streamlit App
st.set_page_config(page_title="YouTube to WAV Converter", layout="centered")
st.title("🎵 YouTube to WAV Converter")
st.write("Converti i video di YouTube in file audio **WAV** di alta qualità.")

# Input dell'utente
url = st.text_input("Inserisci il link del video di YouTube:", placeholder="https://www.youtube.com/watch?v=example")

# Scelta del sampling rate
st.subheader("Configurazione")
sampling_rate = st.radio(
    "Seleziona il sampling rate:",
    options=[44100, 48000],
    format_func=lambda x: f"{x // 1000} kHz",
    index=0
)

# Bottone per avviare la conversione
if st.button("Converti e scarica"):
    if url:
        with st.spinner("Scaricamento e conversione in corso..."):
            result = download_and_convert_to_wav(url, sampling_rate)
        if result:
            st.success("Conversione completata!")
            file_path = os.path.join(OUTPUT_DIR, result)
            # Aggiungi un pulsante per il download
            with open(file_path, "rb") as f:
                st.download_button(
                    label="🎧 Scarica il file WAV",
                    data=f,
                    file_name=result,
                    mime="audio/wav",
                )
    else:
        st.error("Per favore, inserisci un URL valido.")

# Footer
st.markdown("---")
st.markdown(
    "Creato con ❤️ usando [Streamlit](https://streamlit.io/) e [yt-dlp](https://github.com/yt-dlp/yt-dlp)."
)