from gtts import gTTS

alerts = {
    "weapon.mp3": "Warning. Weapon detected.",
    "fight.mp3": "Emergency. Fight detected.",
    "loitering.mp3": "Suspicious loitering detected.",
    "abandoned_object.mp3": "Warning. Unattended object detected."
}

for filename, text in alerts.items():

    tts = gTTS(text=text, lang="en")

    tts.save(f"alerts/sounds/{filename}")

    print(f"Created {filename}")

print("All voice files generated.")