# main.py

def read_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.readlines()
    except (FileNotFoundError, PermissionError) as e:
        print(f'오류: {e}')
    except Exception as e:
        print(f'예상하지 못한 오류 발생: {e}')
    return None

def main():
    print('Hello Mars')

    log_content = read_log_file('mission_computer_main.log')
    if log_content:  
        print('\n[ 로그 파일 내용 출력 (최신순) ]\n')
        for line in reversed(log_content):
            print(line, end='')

if __name__ == '__main__':
    main()