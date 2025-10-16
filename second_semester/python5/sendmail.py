from __future__ import annotations

import smtplib
import ssl
import sys
from email.message import EmailMessage
from getpass import getpass
from socket import gaierror
from typing import Tuple


SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465  # SSL 기본 포트


def build_message(
    sender: str,
    to: str,
    subject: str,
    body: str,
) -> EmailMessage:
    """단순 텍스트 메일 메시지 객체 생성."""
    msg = EmailMessage()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(body)
    return msg


def prompt_credentials() -> Tuple[str, str]:
    """보내는 사람의 계정과 앱 비밀번호를 입력받아 반환."""
    sender = input('보내는 사람 Gmail 주소를 입력하세요: ').strip()
    if not sender:
        print('❌ 보내는 사람 주소는 필수 입력입니다.')
        sys.exit(1)

    app_password = getpass('Gmail 앱 비밀번호(16자리)를 입력하세요: ').strip()
    if not app_password:
        print('❌ 앱 비밀번호는 필수 입력입니다.')
        sys.exit(1)

    return sender, app_password


def send_mail(
    sender: str,
    app_password: str,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """SMTP(SSL)로 메일을 전송하고 주요 예외를 처리한다."""
    msg = build_message(sender, recipient, subject, body)
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=20) as server:
            server.login(sender, app_password)
            server.send_message(msg)
            print('✅ 메일이 성공적으로 전송되었습니다.')

    except smtplib.SMTPAuthenticationError as e:
        print(
            '❌ 로그인 인증 실패.\n'
            '- Gmail 일반 비밀번호는 사용할 수 없습니다.\n'
            '- Google 계정에서 2단계 인증을 활성화하고 앱 비밀번호(16자리)를 발급받아 사용하세요.\n'
            f'- 상세 정보: {e}'
        )
    except smtplib.SMTPRecipientsRefused as e:
        print(f'❌ 받는 사람 주소가 올바르지 않습니다: {recipient}\n상세 정보: {e}')
    except smtplib.SMTPSenderRefused as e:
        print(f'❌ 보내는 사람 주소가 거부되었습니다: {sender}\n상세 정보: {e}')
    except smtplib.SMTPConnectError as e:
        print(f'❌ SMTP 서버({SMTP_SERVER}:{SMTP_PORT})에 연결할 수 없습니다.\n상세 정보: {e}')
    except smtplib.SMTPServerDisconnected as e:
        print(f'❌ 서버 연결이 예기치 않게 끊어졌습니다.\n상세 정보: {e}')
    except (gaierror, TimeoutError) as e:
        print(f'❌ 네트워크 오류입니다. 인터넷 연결 또는 DNS 설정을 확인하세요.\n상세 정보: {e}')
    except Exception as e:
        print(f'❌ 알 수 없는 오류 발생: {e}')


def main() -> None:
    print('=== Gmail SMTP 메일 발송기 (SSL 포트 465) ===')
    sender, app_password = prompt_credentials()

    recipient = input('받는 사람 이메일 주소를 입력하세요: ').strip()
    if not recipient:
        print('❌ 받는 사람 주소는 필수 입력입니다.')
        sys.exit(1)

    subject = input('메일 제목을 입력하세요: ').strip()
    print('메일 본문을 입력하세요. 입력이 끝나면 EOF로 종료합니다.')
    print('(macOS/Linux: Ctrl+D, Windows: Ctrl+Z 후 Enter)')

    try:
        body_lines = sys.stdin.read()
    except KeyboardInterrupt:
        print('\n작업이 취소되었습니다.')
        sys.exit(1)

    send_mail(sender, app_password, recipient, subject, body_lines)


if __name__ == '__main__':
    main()
