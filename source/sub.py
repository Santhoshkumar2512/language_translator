import os
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator
from gtts import gTTS
import tempfile
from playsound import playsound

translator = Translator()

language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    try:
        translated_text = translator.translate(spoken_text, src=from_language, dest=to_language)
        return translated_text.text
    except Exception as e:
        return f"Translation Error: {e}"

def text_to_voice(translated_text):
    try:
        # Create a temporary directory for storing audio data
        temp_dir = tempfile.mkdtemp()
        audio_file = os.path.join(temp_dir, "translated_audio.mp3")

        tts = gTTS(text=translated_text, lang="en")
        tts.save(audio_file)
        
        # Check if the audio file exists
        if os.path.exists(audio_file):
            # Play the audio in runtime
            playsound(audio_file)
        else:
            st.error("Audio file not found.")
    except Exception as e:
        st.error(f"Text-to-Speech Error: {e}")

def main():
    st.title("Language Translator")

    input_option = st.radio("Select Input Option:", ["Speech Recognition", "Text Input"])
    from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()))
    to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()))

    from_language = get_language_code(from_language_name)
    to_language = get_language_code(to_language_name)

    # Ensure that the translations file exists or create it
    translations_file = "translations.txt"
    if not os.path.exists(translations_file):
        open(translations_file, "a").close()

    # Language Swap
    swap_button = st.button("Swap Languages")
    if swap_button:
        from_language_name, to_language_name = to_language_name, from_language_name
        from_language, to_language = to_language, from_language

    if input_option == "Speech Recognition":
        start_button = st.button("Start Translation (Speech Recognition)")
        if start_button:
            st.info("Speak now...")
            with st.spinner("Translating..."):
                rec = sr.Recognizer()
                with sr.Microphone() as source:
                    audio = rec.listen(source)

                try:
                    spoken_text = rec.recognize_google(audio, language=from_language)
                    translated_text = translator_function(spoken_text, from_language, to_language)
                    st.success(f"Translated Text: {translated_text}")
                    
                    # Save Translation
                    if st.button("Save Translation"):
                        with open(translations_file, "a") as file:
                            file.write(f"{spoken_text} -> {translated_text}\n")
                    
                    # Convert translated text to speech
                    text_to_voice(translated_text)
                    
                except sr.UnknownValueError:
                    st.error("Sorry, I could not understand what you said.")
                except sr.RequestError as e:
                    st.error(f"Speech recognition request failed: {e}")
                except PermissionError as e:
                    st.error(f"Permission error: {e}. Please ensure Streamlit has necessary permissions.")
                except Exception as e:
                    st.error(f"Translation error: {e}")
    elif input_option == "Text Input":
        text_input = st.text_area("Enter Text to Translate:")
        translate_button = st.button("Translate Text")
        if translate_button:
            if text_input:
                translated_text = translator_function(text_input, from_language, to_language)
                st.success(f"Translated Text: {translated_text}")
                # Save Translation
                if st.button("Save Translation"):
                    with open(translations_file, "a") as file:
                        file.write(f"{text_input} -> {translated_text}\n")
                # Convert translated text to speech
                text_to_voice(translated_text)
            else:
                st.warning("Please enter text to translate.")

    # Translation History
    if st.checkbox("Show Translation History"):
        with open(translations_file, "r") as file:
            translations = file.readlines()
            for idx, translation in enumerate(translations, 1):
                st.write(f"{idx}. {translation.strip()}")

if __name__ == "__main__":
    main()
