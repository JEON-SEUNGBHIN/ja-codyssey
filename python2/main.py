# main.py

# CSV 파일을 읽고, 목록을 리스트로 변환
def read_csv(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 첫 번째 줄(헤더) 가져오기
        headers = lines[0].strip().split(',')

        # 데이터 변환 (리스트 컴프리헨션 활용)
        data = [
            {headers[i]: (float(fields[i]) if headers[i] == 'Flammability' else fields[i]) for i in range(len(headers))}
            for line in lines[1:] if (fields := line.strip().split(','))
        ]

        return data

    except (FileNotFoundError, PermissionError) as e:
        print(f'오류: {e}')
    except ValueError:
        print('오류: CSV 파일 내 숫자 변환 실패')
    except Exception as e:
        print(f'예상하지 못한 오류 발생: {e}')
    
    return None

# 리스트를 인화성 지수가 높은 순으로 정렬
def sort_by_flammability(items):
    return sorted(items, key=lambda x: x['Flammability'], reverse=True)

# 인화성 지수가 0.7 이상인 항목 필터링
def filter_dangerous_items(items):
    return [item for item in items if item['Flammability'] >= 0.7]

# 리스트를 CSV 파일로 저장 (모든 컬럼 포함)
def save_to_csv(filename, headers, items):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(','.join(headers) + '\n')
            file.writelines(','.join(str(item[h]) for h in headers) + '\n' for item in items)
        print(f'\n"{filename}" 파일이 생성되었습니다.')
    except Exception as e:
        print(f'오류 발생: {e}')

# 리스트를 텍스트 기반의 이진 파일(.bin)로 저장      
def save_to_binary_file(filename, items):
    try:
        with open(filename, 'wb') as file:
            for item in items:
                line = ', '.join(f'{k}: {v}' for k, v in item.items())
                file.write((line + '\n').encode('utf-8'))
        print(f'\n"{filename}" 이진 파일이 생성되었습니다.')
    except Exception as e:
        print(f'이진 파일 저장 중 오류 발생: {e}')

# 이진 파일 출력    
def read_from_binary_file(filename):
    try:
        with open(filename, 'rb') as file:
            lines = file.readlines()
        print(f'\n=== 이진 파일 "{filename}"의 내용 ===')
        for line in lines:
            print(line.decode('utf-8').strip())
    except Exception as e:
        print(f'이진 파일 읽기 중 오류 발생: {e}')

# 파일 읽기
inventory = read_csv('Mars_Base_Inventory_List.csv')

if inventory:
    
    # 인화성이 높은 순으로 정렬
    sorted_inventory = sort_by_flammability(inventory)

    # 인화성 지수 0.7 이상 필터링
    dangerous_items = filter_dangerous_items(sorted_inventory)

    # 결과 출력 (모든 컬럼 유지)
    print('\n=== 원본 CSV 파일 내용 ===')
    for item in inventory:
        print(', '.join(f"{k}: {v}" for k, v in item.items()))

    print('\n=== 정렬된 화물 목록 (인화성 높은 순) ===')
    print('\n'.join(', '.join(f"{k}: {v}" for k, v in item.items()) for item in sorted_inventory))

    print('\n=== 인화성 0.7 이상 화물 목록 ===')
    print('\n'.join(', '.join(f"{k}: {v}" for k, v in item.items()) for item in dangerous_items))

    # 위험 목록 CSV 파일 저장 (모든 컬럼 포함)
    save_to_csv('Mars_Base_Inventory_danger.csv', inventory[0].keys(), dangerous_items)

    # 이진 파일 저장 (UTF-8 인코딩된 텍스트 기반)
    save_to_binary_file('Mars_Base_Inventory_List.bin', sorted_inventory)

    # 이진 파일 출력
    read_from_binary_file('Mars_Base_Inventory_List.bin')
