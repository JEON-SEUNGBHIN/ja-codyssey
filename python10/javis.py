import os
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write

class VoiceRecorder:
    def __init__(self, sample_rate=44100, directory='records'):
        self.sample_rate = sample_rate
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def record(self, duration=5):
        print('녹음 시작...')
        data = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=1, dtype='int16')
        sd.wait()

        filename = datetime.now().strftime('%Y%m%d-%H%M%S') + '.wav'
        filepath = os.path.join(self.directory, filename)
        write(filepath, self.sample_rate, data)
        print(f'저장 완료: {filepath}')

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
    print('작업을 선택하세요:\n1. 음성 녹음\n2. 날짜 범위로 파일 목록 확인')
    choice = input('선택 (1 또는 2): ')

    if choice == '1':
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
    else:
        print('잘못된 선택입니다.')

if __name__ == '__main__':
    main()
