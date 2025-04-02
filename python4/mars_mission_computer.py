import time

# Sensor 클래스
class Sensor:
    def __init__(self, name, label, unit, min_val, max_val, round_digits):
        self.name = name
        self.label = label
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.round_digits = round_digits
        self.value = None

    def update(self):
        self.value = round(
            self.min_val + (self.max_val - self.min_val) * (time.time() % 1),
            self.round_digits
        )

    def to_log(self):
        if self.value is None:
            return f'  {self.label}: (측정되지 않음)'
        return f'  {self.label}: {self.value}{self.unit}'


# DummySensor 클래스
class DummySensor:
    def __init__(self):
        self.sensors = [
            Sensor('mars_base_internal_temperature', '화성 기지 내부 온도', '°C', 18, 30, 2),
            Sensor('mars_base_external_temperature', '화성 기지 외부 온도', '°C', 0, 21, 2),
            Sensor('mars_base_internal_humidity', '화성 기지 내부 습도', '%', 50, 60, 2),
            Sensor('mars_base_external_illuminance', '화성 기지 외부 광량', 'W/m²', 500, 715, 2),
            Sensor('mars_base_internal_co2', '화성 기지 내부 이산화탄소 농도', '%', 0.02, 0.1, 3),
            Sensor('mars_base_internal_oxygen', '화성 기지 내부 산소 농도', '%', 4, 7, 2),
        ]

    def set_env(self):
        for sensor in self.sensors:
            sensor.update()

    def get_env(self):
        self.set_env()
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        log_lines = [f'=== {now} 센서 데이터 ===']
        env_data = {}

        for sensor in self.sensors:
            log_lines.append(sensor.to_log())
            env_data[sensor.name] = sensor.value

        with open('log_record.log', 'a') as file:
            file.write('\n'.join(log_lines) + '\n\n')

        for line in log_lines:
            print(line)
        print()   # 터미널 줄바꿈

        return env_data


# MissionComputer 클래스
class MissionComputer:
    def __init__(self, ds):
        self.ds = ds
        self.env_values = {}

    def get_sensor_data(self):
        self.env_values = self.ds.get_env()
        return self.env_values


# 평균 출력
def print_and_log_average(data_list, sensors):
    average = {}
    count = len(data_list)

    for data in data_list:
        for key in data:
            average[key] = average.get(key, 0) + data[key]

    for key in average:
        average[key] = round(average[key] / count, 3)

    now = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f'=== {now} 평균 센서 값 ===')
    log_lines = [f'=== {now} 평균 센서 값 ===']

    for sensor in sensors:
        val = average.get(sensor.name)
        if val is not None:
            line = f'  {sensor.label}: {val}{sensor.unit}'
            print(line)
            log_lines.append(line)

    with open('log_record.log', 'a') as file:
        file.write('\n'.join(log_lines) + '\n\n')

if __name__ == '__main__':
    ds = DummySensor()
    mc = MissionComputer(ds)
    collected = []

    print('실행 중입니다. 종료하려면 Window는 Ctrl + C / Mac은 Control + C 를 누르세요.\n')
    
    try:
        while True:
            env = mc.get_sensor_data()
            collected.append(env)

            if len(collected) >= 5:
                print_and_log_average(collected, ds.sensors)
                collected.clear()

            # 60초 동안 1초씩 쉬면서 Ctrl+C 감지
            for _ in range(60):
                time.sleep(1)

    except KeyboardInterrupt:
        print('\nSystem stopped....')
