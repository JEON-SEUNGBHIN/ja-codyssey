import platform
import os
import json
import time


class MissionComputer:
    def __init__(self):
        # 설정 파일 로드
        self.settings = self.load_settings()

    def load_settings(self):
        """
        setting.txt 파일로부터 출력할 항목 설정을 불러온다.
        설정이 없으면 기본값(True)으로 모든 항목 출력.
        """
        settings = {
            'os': True,
            'os_version': True,
            'cpu_type': True,
            'cpu_cores': True,
            'memory_total': True,
            'cpu_usage': True,
            'memory_usage': True
        }
        try:
            with open('setting.txt', 'r') as file:
                for line in file:
                    key_value = line.strip().split('=')
                    if len(key_value) == 2:
                        key, value = key_value
                        settings[key.strip()] = value.strip().lower() == 'true'
        except FileNotFoundError:
            # 설정 파일 없으면 기본값 사용
            pass
        return settings

    def get_mission_computer_info(self):
        """
        OS, CPU, 메모리 등의 시스템 기본 정보를 JSON 형식으로 출력한다.
        운영체제 종류에 따라 메모리 정보 수집 방식이 다름.
        """
        try:
            info = {}

            if self.settings.get('os'):
                info['os'] = platform.system()

            if self.settings.get('os_version'):
                info['os_version'] = platform.version()

            if self.settings.get('cpu_type'):
                info['cpu_type'] = platform.processor()

            if self.settings.get('cpu_cores'):
                info['cpu_cores'] = os.cpu_count()

            if self.settings.get('memory_total'):
                os_type = platform.system()

                # Windows의 메모리 정보 가져오기
                if os_type == 'Windows':
                    import ctypes

                    class MEMORYSTATUS(ctypes.Structure):
                        _fields_ = [
                            ('dwLength', ctypes.c_uint),
                            ('dwMemoryLoad', ctypes.c_uint),
                            ('dwTotalPhys', ctypes.c_size_t),
                            ('dwAvailPhys', ctypes.c_size_t),
                            ('dwTotalPageFile', ctypes.c_size_t),
                            ('dwAvailPageFile', ctypes.c_size_t),
                            ('dwTotalVirtual', ctypes.c_size_t),
                            ('dwAvailVirtual', ctypes.c_size_t),
                        ]

                    memory = MEMORYSTATUS()
                    memory.dwLength = ctypes.sizeof(MEMORYSTATUS)
                    ctypes.windll.kernel32.GlobalMemoryStatus(ctypes.byref(memory))
                    info['memory_total'] = memory.dwTotalPhys

                # Linux 메모리 정보
                elif os_type == 'Linux':
                    with open('/proc/meminfo', 'r') as mem:
                        for line in mem:
                            if 'MemTotal' in line:
                                info['memory_total'] = int(line.split()[1]) * 1024
                                break

                # macOS (Darwin) 메모리 정보
                elif os_type == 'Darwin':
                    mem_bytes = int(os.popen("sysctl -n hw.memsize").read())
                    info['memory_total'] = mem_bytes

        except Exception as e:
            info['error'] = str(e)

        print(json.dumps(info, indent=2))
        return info

    def get_mission_computer_load(self):
        """
        CPU 사용률과 메모리 사용률을 실시간으로 측정하여 JSON 형식으로 출력한다.
        운영체제마다 방식이 다름.
        """
        try:
            load = {}
            os_type = platform.system()

            # CPU 사용률
            if self.settings.get('cpu_usage'):
                if os_type == 'Windows':
                    cpu_output = os.popen('wmic cpu get loadpercentage').read().splitlines()
                    for line in cpu_output:
                        if line.strip().isdigit():
                            load['cpu_usage'] = line.strip() + '%'
                            break

                elif os_type == 'Linux':
                    # CPU 사용률 측정 (1초 간격)
                    with open('/proc/stat', 'r') as f:
                        fields1 = f.readline().strip().split()[1:]
                        fields1 = list(map(int, fields1))
                    time.sleep(1)
                    with open('/proc/stat', 'r') as f:
                        fields2 = f.readline().strip().split()[1:]
                        fields2 = list(map(int, fields2))
                    idle1 = fields1[3]
                    idle2 = fields2[3]
                    total1 = sum(fields1)
                    total2 = sum(fields2)
                    cpu_usage = 100 * (1 - (idle2 - idle1) / (total2 - total1))
                    load['cpu_usage'] = f'{cpu_usage:.2f}%'

                elif os_type == 'Darwin':
                    # macOS에서는 ps 명령어를 통해 전체 프로세스 CPU 합산
                    cpu_output = os.popen("ps -A -o %cpu | awk '{s+=$1} END {print s}'").read().strip()
                    load['cpu_usage'] = f'{float(cpu_output):.2f}%'

            # 메모리 사용률
            if self.settings.get('memory_usage'):
                if os_type == 'Windows':
                    import ctypes

                    class MEMORYSTATUS(ctypes.Structure):
                        _fields_ = [
                            ('dwLength', ctypes.c_uint),
                            ('dwMemoryLoad', ctypes.c_uint),
                            ('dwTotalPhys', ctypes.c_size_t),
                            ('dwAvailPhys', ctypes.c_size_t),
                            ('dwTotalPageFile', ctypes.c_size_t),
                            ('dwAvailPageFile', ctypes.c_size_t),
                            ('dwTotalVirtual', ctypes.c_size_t),
                            ('dwAvailVirtual', ctypes.c_size_t),
                        ]

                    memory = MEMORYSTATUS()
                    memory.dwLength = ctypes.sizeof(MEMORYSTATUS)
                    ctypes.windll.kernel32.GlobalMemoryStatus(ctypes.byref(memory))
                    load['memory_usage'] = f'{memory.dwMemoryLoad}%'

                elif os_type == 'Linux':
                    with open('/proc/meminfo', 'r') as mem:
                        total = available = None
                        for line in mem:
                            if 'MemTotal' in line:
                                total = int(line.split()[1])
                            elif 'MemAvailable' in line:
                                available = int(line.split()[1])
                            if total and available:
                                break
                        mem_usage = 100 * (1 - (available / total))
                        load['memory_usage'] = f'{mem_usage:.2f}%'

                elif os_type == 'Darwin':
                    mem_total = int(os.popen("sysctl -n hw.memsize").read())
                    vm_stats = os.popen("vm_stat").read()
                    free_pages = 0
                    for line in vm_stats.splitlines():
                        if 'Pages free' in line:
                            free_pages = int(line.split(":")[1].strip().replace('.', ''))
                            break
                    free_bytes = free_pages * 4096
                    mem_usage = 100 * (1 - (free_bytes / mem_total))
                    load['memory_usage'] = f'{mem_usage:.2f}%'

        except Exception as e:
            load['error'] = str(e)

        print(json.dumps(load, indent=2))
        return load


if __name__ == '__main__':
    # 인스턴스 생성 및 정보 출력
    runComputer = MissionComputer()
    runComputer.get_mission_computer_info()
    runComputer.get_mission_computer_load()
