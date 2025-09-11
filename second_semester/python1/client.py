from __future__ import annotations

import socket
import threading
import sys


def receive_loop(sock: socket.socket) -> None:
    while True:
        try:
            data = sock.recv(4096)
        except OSError:
            break
        if not data:
            break
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            text = data.decode("utf-8", errors="replace")
        print(text, end="")
    print("\n[INFO] 서버와의 연결이 종료되었습니다.")


def main() -> None:
    if len(sys.argv) < 4:
        print("사용법: python client.py <host> <port> <닉네임>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    # 서버가 먼저 묻는 프롬프트 수신 후 닉네임 전송
    _ = sock.recv(1024)
    sock.sendall((name + "\n").encode("utf-8"))

    # 수신 전용 스레드 시작
    threading.Thread(target=receive_loop, args=(sock,), daemon=True).start()

    try:
        while True:
            line = input()
            if not line:
                continue
            sock.sendall((line + "\n").encode("utf-8"))
            if line == "/종료":
                break
    except (KeyboardInterrupt, EOFError):
        try:
            sock.sendall("/종료\n".encode("utf-8"))
        except OSError:
            pass
    finally:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        sock.close()


if __name__ == "__main__":
    main()
