from gtts import gTTS
from io import BytesIO

def generate_voice(text):

    tts = gTTS(
        text=text,
        lang="en"
    )

    audio_bytes = BytesIO()

    tts.write_to_fp(audio_bytes)

    audio_bytes.seek(0)

    return audio_bytes