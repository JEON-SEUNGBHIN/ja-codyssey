# 시스템 정보 획득은 허용되므로 platform과 os는 import 유지
import platform
import os


class MissionComputer:
    def __init__(self):
        # 출력 항목 기본 설정값: 모두 True로 설정
        self.settings = {
            'os': True,
            'os_version': True,
            'cpu_type': True,
            'cpu_cores': True,
            'memory_total': True,
            'cpu_usage': True,
            'memory_usage': True
        }
        # 설정 파일을 불러와 사용자 설정값 반영
        self.load_settings()

    def load_settings(self):
        """
        setting.txt 파일에서 항목별 출력 여부(True/False)를 읽어 self.settings에 반영한다.
        파일이 없으면 기본값(True) 유지.
        """
        try:
            f = open('setting.txt', 'r')        # 설정 파일 열기
            lines = f.readlines()               # 모든 줄 읽기
            f.close()
            for line in lines:
                parts = line.strip().split('=')  # 'key=value' 형태로 분리
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().lower()
                    self.settings[key] = (value == 'true')  # True 또는 False로 설정
        except:
            pass  # 설정 파일이 없거나 오류가 있어도 무시

    def get_mission_computer_info(self):
        """
        운영체제, CPU 정보, 메모리 총량 등 시스템 기본 정보를 수집하여 출력한다.
        출력은 JSON과 유사한 문자열 포맷으로 직접 구성.
        """
        info = '{\n'  # 출력 시작

        # 운영체제 이름 (예: Windows, Linux, Darwin)
        if self.settings.get('os'):
            info += f'  "os": "{platform.system()}",\n'

        # 운영체제 버전 정보
        if self.settings.get('os_version'):
            info += f'  "os_version": "{platform.version()}",\n'

        # CPU 종류 (Intel, arm64 등)
        if self.settings.get('cpu_type'):
            info += f'  "cpu_type": "{platform.processor()}",\n'

        # CPU 코어 개수
        if self.settings.get('cpu_cores'):
            info += f'  "cpu_cores": {os.cpu_count()},\n'

        # 메모리 총량 (Byte 단위)
        if self.settings.get('memory_total'):
            try:
                os_type = platform.system()
                mem_total = 0

                if os_type == 'Windows':
                    # Windows에서는 ctypes 사용하여 시스템 API로 메모리 정보 획득
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
                    mem_total = memory.dwTotalPhys

                elif os_type == 'Linux':
                    # /proc/meminfo 파일에서 MemTotal 읽기
                    f = open('/proc/meminfo', 'r')
                    for line in f:
                        if 'MemTotal' in line:
                            mem_total = int(line.split()[1]) * 1024  # KB → Byte
                            break
                    f.close()

                elif os_type == 'Darwin':
                    # macOS는 sysctl 명령어로 메모리 크기 획득
                    mem_total = int(os.popen("sysctl -n hw.memsize").read())

                info += f'  "memory_total": {mem_total},\n'

            except:
                info += '  "memory_total": "ERROR",\n'

        # 마지막 쉼표 제거 후 닫기
        if info.endswith(',\n'):
            info = info[:-2] + '\n'
        info += '}\n'
        print(info)

    def get_mission_computer_load(self):
        """
        실시간 CPU 및 메모리 사용률을 측정하여 출력한다.
        Linux의 CPU 사용률은 time.sleep()이 필요하여 이 버전에서는 제외함.
        """
        os_type = platform.system()
        load = '{\n'  # 출력 시작

        # CPU 사용률 측정
        if self.settings.get('cpu_usage'):
            try:
                cpu_usage = None

                if os_type == 'Windows':
                    # Windows: wmic 명령어로 CPU 부하 조회
                    output = os.popen('wmic cpu get loadpercentage').read().splitlines()
                    for line in output:
                        if line.strip().isdigit():
                            cpu_usage = line.strip() + '%'
                            break

                elif os_type == 'Darwin':
                    # macOS: 모든 프로세스의 %CPU 합산
                    usage = os.popen("ps -A -o %cpu | awk '{s+=$1} END {print s}'").read().strip()
                    cpu_usage = f'{float(usage):.2f}%'

                # Linux는 time 모듈 제거되어 측정 불가

                if cpu_usage:
                    load += f'  "cpu_usage": "{cpu_usage}",\n'
            except:
                load += '  "cpu_usage": "ERROR",\n'

        # 메모리 사용률 측정
        if self.settings.get('memory_usage'):
            try:
                mem_usage = None

                if os_type == 'Windows':
                    # Windows: ctypes 사용
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
                    mem_usage = f'{memory.dwMemoryLoad}%'

                elif os_type == 'Linux':
                    # /proc/meminfo에서 MemTotal, MemAvailable 읽어서 계산
                    total = available = 0
                    f = open('/proc/meminfo', 'r')
                    for line in f:
                        if 'MemTotal' in line:
                            total = int(line.split()[1])
                        elif 'MemAvailable' in line:
                            available = int(line.split()[1])
                        if total and available:
                            break
                    f.close()
                    mem_usage = f'{(100 * (1 - available / total)):.2f}%'

                elif os_type == 'Darwin':
                    # macOS: vm_stat 명령어로 free page 수 계산
                    mem_total = int(os.popen("sysctl -n hw.memsize").read())
                    stats = os.popen("vm_stat").read()
                    free_pages = 0
                    for line in stats.splitlines():
                        if 'Pages free' in line:
                            free_pages = int(line.split(":")[1].strip().replace('.', ''))
                            break
                    free_bytes = free_pages * 4096
                    mem_usage = f'{(100 * (1 - free_bytes / mem_total)):.2f}%'

                if mem_usage:
                    load += f'  "memory_usage": "{mem_usage}",\n'
            except:
                load += '  "memory_usage": "ERROR",\n'

        # 마지막 쉼표 제거 후 닫기
        if load.endswith(',\n'):
            load = load[:-2] + '\n'
        load += '}\n'
        print(load)


# 프로그램 진입점
if __name__ == '__main__':
    runComputer = MissionComputer()              # 인스턴스 생성
    runComputer.get_mission_computer_info()      # 시스템 기본 정보 출력
    runComputer.get_mission_computer_load()      # 실시간 부하 정보 출력
