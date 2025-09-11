def caesar_cipher_decode(target_text, shift):
    decoded = ''
    for char in target_text:
        if 'a' <= char <= 'z':
            decoded += chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
        elif 'A' <= char <= 'Z':
            decoded += chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
        else:
            decoded += char
    return decoded


def main():
    try:
        with open('password.txt', 'r') as f:
            encrypted_text = f.read().strip()
    except FileNotFoundError:
        print('오류: password.txt 파일이 존재하지 않습니다.')
        return
    except Exception as e:
        print(f'예상치 못한 오류 발생: {e}')
        return

    dictionary = [
        'emergency', 'doctor', 'password', 'help',
        'mars', 'danger', 'base', 'security'
    ]

    print('자리수별 복호화 결과:\n')

    for shift in range(26):
        result = caesar_cipher_decode(encrypted_text, shift)
        print(f'[{shift}] {result}')

        lower_result = result.lower()
        if any(word in lower_result for word in dictionary):
            print(f'\n자동 탐지됨! shift={shift}에서 사전 단어 발견.')
            try:
                with open('result.txt', 'w') as out:
                    out.write(result)
                print('복호화 결과가 result.txt에 저장되었습니다.')
            except Exception as e:
                print(f'파일 저장 중 오류 발생: {e}')
            return

    print('\n자동 매칭된 단어가 없어 사람이 직접 확인해야 합니다.')

    try:
        selected = int(input('복호화된 shift 번호를 입력하세요: '))
        if not (0 <= selected < 26):
            print('유효하지 않은 번호입니다.')
            return

        final = caesar_cipher_decode(encrypted_text, selected)
        with open('result.txt', 'w') as f:
            f.write(final)
        print('복호화 결과가 result.txt에 저장되었습니다.')
    except Exception as e:
        print(f'입력 또는 저장 중 오류 발생: {e}')


if __name__ == '__main__':
    main()
