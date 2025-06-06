import os
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import csv
import wave
import numpy as np

class VoiceRecorder:
    def __init__(self, sample_rate=44100, directory='records', transcript_file='transcripts.csv', input_device=2):
        self.sample_rate = sample_rate
        self.directory = directory
        self.transcript_file = transcript_file
        self.input_device = input_device
        os.makedirs(self.directory, exist_ok=True)

        if self.input_device is not None:
            sd.default.device = (self.input_device, None)

    def list_input_devices(self):
        print("사용 가능한 입력 장치 목록:")
        for i, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                print(f"{i}: {device['name']}")

    def record(self, duration=5):
        print('녹음 시작...')
        sd.default.samplerate = self.sample_rate
        sd.default.channels = 1
        data = sd.rec(int(duration * self.sample_rate), dtype='float32')
        sd.wait()

        filename = datetime.now().strftime('%Y%m%d-%H%M%S') + '.wav'
        filepath = os.path.join(self.directory, filename)
        self.save_wav(filepath, data)
        print(f'저장 완료: {filepath}')

    def save_wav(self, filepath, data):
        data_int16 = (data * 32767).astype('int16')
        with wave.open(filepath, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(data_int16.tobytes())

    def transcribe(self, filepath):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 100

        with sr.AudioFile(filepath) as source:
            duration = source.DURATION
            print(f'[{os.path.basename(filepath)}] 파일 길이: {duration:.2f}초')
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio, language='ko-KR')
            print(f'인식된 텍스트: {text}')
        except sr.UnknownValueError:
            text = '[인식 실패]'
        except sr.RequestError as e:
            text = f'[요청 실패: {e}]'

        filename = os.path.basename(filepath)
        timestamp = filename[:15]
        self.save_transcript(timestamp, filename, text)

    def save_transcript(self, timestamp, filename, text):
        with open(self.transcript_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, filename, text])

    def transcribe_existing_files(self):
        for filename in os.listdir(self.directory):
            if filename.endswith('.wav'):
                filepath = os.path.join(self.directory, filename)
                self.transcribe(filepath)

    def search_keyword(self, keyword):
        if not os.path.exists(self.transcript_file):
            print('CSV 파일이 존재하지 않습니다.')
            return

        with open(self.transcript_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            print(f"키워드 '{keyword}' 검색 결과:")
            for row in reader:
                if keyword in row[2]:
                    print(f'{row[0]} | {row[1]} | {row[2]}')

    def list_files_by_date_range(self, start_date, end_date):
        if not os.path.exists(self.directory):
            return []

        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')

        matched_files = []
        for filename in os.listdir(self.directory):
            if filename.endswith('.wav'):
                try:
                    file_dt = datetime.strptime(filename[:15], '%Y%m%d-%H%M%S')
                    if start_dt.date() <= file_dt.date() <= end_dt.date():
                        matched_files.append(filename)
                except ValueError:
                    continue

        return matched_files

def main():
    recorder = VoiceRecorder()
    print('작업을 선택하세요:\n0. 입력 장치 목록 보기\n1. 음성 녹음\n2. 날짜 범위로 파일 목록 확인\n3. 키워드로 CSV 검색\n4. 기존 녹음 파일 STT 처리')
    choice = input('선택 (0, 1, 2, 3 또는 4): ')

    if choice == '0':
        recorder.list_input_devices()
    elif choice == '1':
        try:
            duration = int(input('녹음 시간(초): '))
        except ValueError:
            print('숫자를 입력하세요.')
            return
        recorder.record(duration)
    elif choice == '2':
        start_date = input('시작 날짜 (YYYY-MM-DD): ')
        end_date = input('종료 날짜 (YYYY-MM-DD): ')
        files = recorder.list_files_by_date_range(start_date, end_date)
        print('\n선택한 날짜 범위의 파일 목록:')
        for f in files:
            print(f)
    elif choice == '3':
        keyword = input('검색할 키워드: ')
        recorder.search_keyword(keyword)
    elif choice == '4':
        recorder.transcribe_existing_files()
    else:
        print('잘못된 선택입니다.')

if __name__ == '__main__':
    main()
