# mars_mission_computer.py

import random
import time

# 하나의 센서를 표현하는 클래스
class Sensor:
  def __init__(self, name, label, unit, min_val, max_val, round_digits):
    self.name = name  # 센서의 내부 이름
    self.label = label # 출력용 이름
    self.unit = unit # 단위
    self.min_val = min_val # 최소값
    self.max_val = max_val # 최대값
    self.round_digits = round_digits # 소수점 자리수
    self.value = None # 초기에는 측정되지 않은 상태라는 뜻으로 None 저장

  # 센서값을 랜덤으로 생성하여 value에 저장
  def update(self):
    self.value = round(random.uniform(self.min_val, self.max_val), self.round_digits)

  # 센서값을 출력용 로그 문자열로 반환
  def log(self):
    # 아직 측정되지 않았을 경우
    if self.value is None:
      return f'{self.label}: 아직 측정되지 않음'
    # 값이 있는 경우
    return f'  {self.label}: {self.value}{self.unit}'

# 여러 개의 센서를 관리하는 클래스
class DummySensor:
  def __init__(self):
    # 센서 목록 생성(Sensor 객체 6개를 리스트에 저장)
    self.sensors = [
      Sensor('mars_base_internal_temperature', '화성 기지 내부 온도', '°C', 18, 30, 2),
      Sensor('mars_base_external_temperature', '화성 기지 외부 온도', '°C', 0, 21, 2),
      Sensor('mars_base_internal_humidity', '화성 기지 내부 습도', '%', 50, 60, 2),
      Sensor('mars_base_external_illuminance', '화성 기지 외부 광량', 'W/m2', 500, 715, 2),
      Sensor('mars_base_internal_co2', '화성 기지 내부 이산화탄소 농도', '%', 0.02, 0.1, 3),      
      Sensor('mars_base_internal_oxygen', '화성 기지 내부 산소 농도', '%', 4, 7, 2)
    ]

  # 모든 센서의 값을 랜덤으로 설정 (update 호출)
  def set_env(self):
    for sensor in self.sensors:
      sensor.update()

  # 센서값을 로그에 저장하고, 딕셔너리로 반환
  def get_env(self): 
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')

    # 로그 라인(시간) 
    log_lines =[f'=== {current_time} 센서 데이터 ===\n']
    
    # 센서별 로그 문자열 생성
    for sensor in self.sensors:
      log_lines.append(sensor.log())

    # 줄바꿈을 사용하여 하나의 문자열로 연결
    log_record = '\n'.join(log_lines) + '\n'

    # 로그 파일에 내용 추가로 기록
    with open('log_record.log', 'a') as file: 
      file.write(log_record)

    # 측정된 센서값만 딕셔너리 형태로 반환(None 값은 제외)
    return {
      sensor.name: sensor.value
      for sensor in self.sensors
      if sensor.value is not None
    }
  
# 실행 부분
if __name__ == '__main__':
  ds = DummySensor()       # 인스턴스 생성
  ds.set_env()             # set_env 호출(센서 값 설정)
  result = ds.get_env()    # get_env 호출(센서 값 가져오기 및 로그 저장)
  print(result)            # 결과 출력
