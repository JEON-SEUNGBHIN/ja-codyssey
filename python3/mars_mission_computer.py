# mars_mission_computer.py

import random
import time

class DummySensor:

  # 센서 데이터 딕셔너리 초기화
  def __init__(self):
    self.env_values = {
      'mars_base_internal_temperature': 0.0, # 화성 기지 내부 온도
      'mars_base_external_temperature': 0.0, # 화성 기지 외부 온도
      'mars_base_internal_humidity': 0.0, # 화성 기지 내부 습도
      'mars_base_external_illuminance': 0.0, # 화성 기지 외부 광량
      'mars_base_internal_co2': 0.0, # 화성 기지 내부 이산화탄소 농도
      'mars_base_internal_oxygen': 0.0, # 화성 기지 내부 산소 농도
    }

  # 각 항목 데이터를 랜덤으로 생성
  def set_env(self):
    self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30),2) # 소수점 둘째 자리까지만 반올림해서 반환
    self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21),2) # 소수점 둘째 자리까지만 반올림해서 반환
    self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60),2) # 소수점 둘째 자리까지만 반올림해서 반환
    self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715),2) # 소수점 둘째 자리까지만 반올림해서 반환
    self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1),3) # 소수점 셋째 자리까지만 반올림해서 반환
    self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7),2) # 소수점 둘째 자리까지만 반올림해서 반환

  # env_values를 반환하고 로그 파일에 기록
  def get_env(self): 
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')

    log_record = (
    f"=== {current_time} 센서 데이터 ===\n "
    f" 화성 기지 내부 온도: {self.env_values['mars_base_internal_temperature']}°C\n "
    f" 화성 기지 외부 온도: {self.env_values['mars_base_external_temperature']}°C\n "
    f" 화성 기지 내부 습도: {self.env_values['mars_base_internal_humidity']}%\n "
    f" 화성 기지 외부 광량: {self.env_values['mars_base_external_illuminance']}W/m2\n "
    f" 화성 기지 내부 이산화탄소 농도: {self.env_values['mars_base_internal_co2']}%\n "
    f" 화성 기지 외부 산소 농도: {self.env_values['mars_base_internal_oxygen']}%\n "
    f'\n'
  )
  #   
    with open('log_record.log','a') as file:
      file.write(log_record)

    return self.env_values
  
# 실행 부분
if __name__ == '__main__':
  ds = DummySensor()       # 인스턴스 생성
  ds.set_env()             # set_env 호출(센서 값 설정)
  result = ds.get_env()    # get_env 호출(센서 값 가져오기 및 로그 저장)
  print(result)            # 결과 출력
