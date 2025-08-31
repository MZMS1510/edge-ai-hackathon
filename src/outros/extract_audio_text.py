import speech_recognition as sr
import os

# Caminho absoluto da raiz do projeto (duas pastas acima deste script)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
audio_dir = os.path.join(ROOT_DIR, 'assets', 'Estudos-livros', 'audios')
output_txt = os.path.join(ROOT_DIR, 'assets', 'Estudos-livros', 'audios_transcritos.txt')

recognizer = sr.Recognizer()
all_texts = []

for filename in os.listdir(audio_dir):
    if filename.lower().endswith(('.wav', '.aiff', '.flac')):
        audio_path = os.path.join(audio_dir, filename)
        print(f'Transcrevendo: {audio_path}')
        try:
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
            texto = recognizer.recognize_google(audio, language='en-US')
            all_texts.append(f'Arquivo: {filename}\n{texto}\n')
        except sr.UnknownValueError:
            all_texts.append(f'Arquivo: {filename}\n[Não foi possível entender o áudio]\n')
        except sr.RequestError as e:
            all_texts.append(f'Arquivo: {filename}\n[Erro ao requisitar resultados: {e}]\n')

with open(output_txt, 'w', encoding='utf-8') as f:
    f.write('\n'.join(all_texts))
print(f'Todas as transcrições foram salvas em {output_txt}')
