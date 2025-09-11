from __future__ import annotations

import argparse
import socket
import threading
from typing import Dict, Tuple

VERSION = "chat-server 1.1"
Address = Tuple[str, int]


class ChatServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Dict[socket.socket, str] = {}
        self.lock = threading.Lock()

    def start(self) -> None:
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"[INFO] {VERSION} 시작: {self.host}:{self.port}")
        try:
            while True:
                client_sock, addr = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client, args=(client_sock, addr), daemon=True
                ).start()
        except KeyboardInterrupt:
            print("\n[INFO] 서버 종료 중...")
        finally:
            self.shutdown()

    def broadcast(self, message: str, exclude: socket.socket | None = None) -> None:
        with self.lock:
            dead: list[socket.socket] = []
            for sock in list(self.clients.keys()):
                if exclude is not None and sock is exclude:
                    continue
                try:
                    sock.sendall(message.encode("utf-8"))
                except OSError:
                    dead.append(sock)
            for sock in dead:
                self._safe_remove(sock)

    def _safe_remove(self, sock: socket.socket) -> None:
        name = self.clients.pop(sock, None)
        try:
            sock.close()
        except OSError:
            pass
        if name:
            self.broadcast(f"[시스템] {name}님이 퇴장하셨습니다.\n")
            print(f"[INFO] 연결 종료: {name}")

    def _handle_client(self, client_sock: socket.socket, addr: Address) -> None:
        client_sock.sendall("닉네임을 입력하세요: ".encode("utf-8"))
        try:
            raw = client_sock.recv(1024)
        except OSError:
            client_sock.close()
            return
        if not raw:
            client_sock.close()
            return
        name = raw.decode("utf-8").strip() or f"사용자@{addr[0]}:{addr[1]}"

        with self.lock:
            self.clients[client_sock] = name

        self.broadcast(f"[시스템] {name}님이 입장하셨습니다.\n")
        print(f"[INFO] 연결 수립: {name} {addr}")
        client_sock.sendall(
            f"{VERSION} 접속 완료. '/종료'로 종료, '/w 닉네임 내용'은 귓속말.\n".encode("utf-8")
        )

        while True:
            try:
                data = client_sock.recv(4096)
            except OSError:
                break
            if not data:
                break

            text = data.decode("utf-8").strip()  # CR/LF/공백 모두 제거
            if not text:
                continue

            # 종료 명령: '/종료' 또는 '종료' 허용
            if text in ("/종료", "종료"):
                break

            # ---- 귓속말 파싱(강화) ----
            cmd = text.lstrip()
            # 전각 슬래시(／)나 슬래시 없이 'w '만 입력해도 허용
            if cmd.startswith(("／w ", "/w ", "w ")):
                if cmd[0] in ("/", "／"):
                    cmd = cmd[1:]               # 슬래시 제거 -> 'w ...'
                parts = cmd.split(maxsplit=2)    # ['w', '닉', '내용']
                if len(parts) < 3:
                    client_sock.sendall("[시스템] 사용법: /w 닉네임 내용\n".encode("utf-8"))
                    continue
                _, target_name, msg = parts
                self._whisper(from_name=name, to_name=target_name, msg=msg,
                              from_sock=client_sock)
                continue
            # ---------------------------

            # 일반 브로드캐스트
            self.broadcast(f"{name}> {text}\n")

        self._safe_remove(client_sock)

    def _whisper(
        self,
        from_name: str,
        to_name: str,
        msg: str,
        from_sock: socket.socket | None = None,
    ) -> None:
        target_sock: socket.socket | None = None
        with self.lock:
            for sock, nick in self.clients.items():
                if nick == to_name:
                    target_sock = sock
                    break

        if target_sock is None:
            if from_sock is not None:
                try:
                    from_sock.sendall(
                        f"[시스템] '{to_name}' 사용자를 찾을 수 없습니다.\n".encode("utf-8")
                    )
                except OSError:
                    pass
            return

        # 수신자에게 전달
        try:
            target_sock.sendall(f"[귓속말][{from_name}] {msg}\n".encode("utf-8"))
        except OSError:
            self._safe_remove(target_sock)
            return

        # 발신자에게도 확인용 에코
        if from_sock is not None:
            try:
                from_sock.sendall(f"[귓속말→{to_name}] {msg}\n".encode("utf-8"))
            except OSError:
                pass

    def shutdown(self) -> None:
        with self.lock:
            for sock in list(self.clients.keys()):
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    sock.close()
                except OSError:
                    pass
            self.clients.clear()
        try:
            self.server_socket.close()
        except OSError:
            pass
        print("[INFO] 서버가 종료되었습니다.")


def main() -> None:
    parser = argparse.ArgumentParser(description="멀티스레드 TCP 채팅 서버")
    parser.add_argument("host", help="바인드 호스트 (예: 0.0.0.0)")
    parser.add_argument("port", type=int, help="바인드 포트 (예: 8080)")
    args = parser.parse_args()
    ChatServer(args.host, args.port).start()


if __name__ == "__main__":
    main()
