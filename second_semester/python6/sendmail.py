from __future__ import annotations

import csv
import os
import smtplib
import ssl
import sys
from email.message import EmailMessage
from getpass import getpass
from socket import gaierror
from typing import Dict, Iterable, List, Tuple


DEFAULT_CSV = 'mail_target_list.csv'

SMTP_PRESET = {
    'gmail': ('smtp.gmail.com', 465),
    'naver': ('smtp.naver.com', 465),
}


def prompt_smtp() -> Tuple[str, int, str, str]:
    """SMTP 서버/포트 및 자격 증명을 입력받아 반환."""
    print('=== SMTP 설정 선택 ===')
    print('1) Gmail  2) Naver  3) 사용자 지정')
    choice = input('선택(1/2/3) [1]: ').strip() or '1'

    if choice == '1':
        server, port = SMTP_PRESET['gmail']
    elif choice == '2':
        server, port = SMTP_PRESET['naver']
    else:
        server = input('SMTP 서버 호스트명: ').strip()
        port_str = input('SMTP SSL 포트 [465]: ').strip() or '465'
        try:
            port = int(port_str)
        except ValueError:
            print('❌ 포트 번호가 올바르지 않습니다.')
            sys.exit(1)

    sender = input('보내는 사람 이메일 주소: ').strip()
    if not sender:
        print('❌ 보내는 사람 주소는 필수입니다.')
        sys.exit(1)

    password = getpass('앱 비밀번호 또는 SMTP 비밀번호: ').strip()
    if not password:
        print('❌ 비밀번호는 필수입니다.')
        sys.exit(1)

    return server, port, sender, password


def read_targets(csv_path: str = DEFAULT_CSV) -> List[Tuple[str, str]]:
    """
    CSV에서 (이름, 이메일) 리스트를 읽어 반환.
    헤더 유무를 자동 판별한다.
    """
    if not os.path.exists(csv_path):
        print(f'❌ 대상자 CSV를 찾을 수 없습니다: {csv_path}')
        sys.exit(1)

    targets: List[Tuple[str, str]] = []
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print('❌ CSV가 비어 있습니다.')
        sys.exit(1)

    first = rows[0]
    start_index = 0
    # 헤더 판별: 첫 행 두 번째 값에 '@'가 없으면 헤더로 간주
    if len(first) >= 2 and '@' not in first[1]:
        start_index = 1

    for i, row in enumerate(rows[start_index:], start=start_index + 1):
        if len(row) < 2:
            print(f'⚠️  {i}행을 건너뜁니다(열 부족): {row}')
            continue
        name = row[0].strip()
        email = row[1].strip()
        if not email or '@' not in email:
            print(f'⚠️  {i}행 이메일 형식 오류로 건너뜀: {email}')
            continue
        targets.append((name, email))

    if not targets:
        print('❌ 유효한 메일 대상이 없습니다.')
        sys.exit(1)

    return targets


def load_html_body() -> str:
    """
    HTML 본문을 파일에서 읽거나 표준입력으로 입력받아 반환.
    수신자 이름 치환을 위해 {name} 플레이스홀더를 지원한다.
    """
    path = input('HTML 파일 경로(엔터 시 표준입력 사용): ').strip()
    if path:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()
        except OSError as e:
            print(f'❌ HTML 파일을 읽을 수 없습니다: {e}')
            sys.exit(1)
    else:
        print('HTML 본문을 입력하세요. 종료: macOS/Linux Ctrl+D, Windows Ctrl+Z 후 Enter')
        try:
            html = sys.stdin.read()
        except KeyboardInterrupt:
            print('\n작업이 취소되었습니다.')
            sys.exit(1)

    if not html.strip():
        print('❌ HTML 본문이 비어 있습니다.')
        sys.exit(1)

    return html


def build_html_message(
    sender: str,
    to_addrs: Iterable[str],
    subject: str,
    html_body: str,
) -> EmailMessage:
    """HTML 메일 메시지 객체 생성(텍스트 대체 파트 포함)."""
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = ', '.join(to_addrs)
    msg['Subject'] = subject

    # 기본 텍스트(대체 파트)와 HTML 파트 구성
    msg.set_content('이 메일은 HTML 형식입니다. HTML을 지원하지 않는 클라이언트에서는 내용이 간략히 보일 수 있습니다.')
    msg.add_alternative(html_body, subtype='html')
    return msg


def send_message(
    server_host: str,
    server_port: int,
    sender: str,
    password: str,
    msg: EmailMessage,
) -> None:
    """SMTP over SSL로 메시지 전송."""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(server_host, server_port, context=context, timeout=20) as server:
        server.login(sender, password)
        server.send_message(msg)


def send_bulk_individual(
    server_host: str,
    server_port: int,
    sender: str,
    password: str,
    subject: str,
    html_template: str,
    targets: List[Tuple[str, str]],
) -> None:
    """
    방식 (2): 한 명씩 개별 발송.
    각 수신자에 대해 {name} 플레이스홀더를 치환한다.
    """
    success = 0
    for name, email in targets:
        html = html_template.format(name=name)
        msg = build_html_message(sender, [email], subject, html)
        try:
            send_message(server_host, server_port, sender, password, msg)
            print(f'✅ 전송 성공: {name} <{email}>')
            success += 1
        except smtplib.SMTPAuthenticationError as e:
            print('❌ 인증 실패: 앱 비밀번호/SMTP 설정을 확인하세요.', e)
            break
        except smtplib.SMTPRecipientsRefused as e:
            print(f'❌ 수신자 거부: {email}', e)
        except smtplib.SMTPSenderRefused as e:
            print(f'❌ 발신자 거부: {sender}', e)
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, gaierror, TimeoutError) as e:
            print('❌ 네트워크/서버 오류:', e)
        except Exception as e:
            print('❌ 알 수 없는 오류:', e)

    print(f'=== 개별 발송 결과: {success}/{len(targets)}건 성공 ===')


def send_single_message_to_many(
    server_host: str,
    server_port: int,
    sender: str,
    password: str,
    subject: str,
    html_template: str,
    targets: List[Tuple[str, str]],
) -> None:
    """
    방식 (1): 한 통에 여러 받는 사람을 열거하여 발송.
    이 방식은 개인화({name})가 불가하므로 {name}을 공통 문구로 치환한다.
    """
    emails = [email for _, email in targets]
    common_html = html_template.format(name='고객님')
    msg = build_html_message(sender, emails, subject, common_html)

    try:
        send_message(server_host, server_port, sender, password, msg)
        print(f'✅ 전송 성공: 한 통으로 {len(emails)}명에게 발송')
    except smtplib.SMTPAuthenticationError as e:
        print('❌ 인증 실패: 앱 비밀번호/SMTP 설정을 확인하세요.', e)
    except smtplib.SMTPRecipientsRefused as e:
        print('❌ 일부/전체 수신자 거부:', e)
    except smtplib.SMTPSenderRefused as e:
        print(f'❌ 발신자 거부: {sender}', e)
    except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, gaierror, TimeoutError) as e:
        print('❌ 네트워크/서버 오류:', e)
    except Exception as e:
        print('❌ 알 수 없는 오류:', e)


def main() -> None:
    print('=== HTML 대량 메일러 (표준 라이브러리 / PEP8) ===')
    server, port, sender, password = prompt_smtp()

    csv_path = input(f'대상자 CSV 경로 [{DEFAULT_CSV}]: ').strip() or DEFAULT_CSV
    targets = read_targets(csv_path)

    subject = input('메일 제목: ').strip()
    if not subject:
        print('❌ 제목은 필수입니다.')
        sys.exit(1)

    print('\n본문에서 수신자 이름에는 {name} 플레이스홀더를 사용하세요.')
    print('예: <p>{name}님, 안녕하세요.</p>\n')
    html_template = load_html_body()

    print('\n발송 방식 선택:')
    print('1) 한 통에 여러 받는 사람 열거(개인화 불가)')
    print('2) 한 명씩 반복 발송(개인화 가능)  ← 권장')
    mode = input('선택(1/2) [2]: ').strip() or '2'

    if mode == '1':
        send_single_message_to_many(
            server, port, sender, password, subject, html_template, targets
        )
    else:
        send_bulk_individual(
            server, port, sender, password, subject, html_template, targets
        )


if __name__ == '__main__':
    # 경고 없이 실행되어야 한다는 제약을 만족하도록 작성함.
    main()
