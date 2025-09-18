from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import unquote
import datetime
import json
import mimetypes
import os
import socket
from typing import Dict, Any, Tuple

HOST = ""
PORT = 8080
INDEX_FILE = "index.html"


def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def client_ip(handler: BaseHTTPRequestHandler) -> str:
    # 프록시 환경 고려
    xff = handler.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    xri = handler.headers.get("X-Real-IP")
    if xri:
        return xri.strip()
    return handler.client_address[0]


def geolocate(ip: str) -> Tuple[bool, Dict[str, Any]]:
    """ip-api.com (무료, 무토큰). 성공 시 True와 데이터 반환."""
    url = (
        f"http://ip-api.com/json/{ip}"
        "?fields=status,message,country,regionName,city,lat,lon,timezone,isp,query"
    )
    req = Request(url, headers={"User-Agent": "stdlib-http-server"})
    try:
        with urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode("utf-8", errors="replace"))
            if data.get("status") == "success":
                return True, data
            return False, {"error": data.get("message", "unknown error"), "query": data.get("query")}
    except (HTTPError, URLError, socket.timeout) as e:
        return False, {"error": str(e), "query": ip}


class AppHandler(BaseHTTPRequestHandler):
    server_version = "StdlibHTTP/1.0"

    def log_access(self, status: int) -> None:
        print(f"[ACCESS] {now_str()}  {client_ip(self)}  {self.command} {self.path} -> {status}")

    def send_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.log_access(status)

    def do_GET(self) -> None:
        # 라우팅
        if self.path == "/" or self.path.startswith("/?"):
            return self.serve_index()
        if self.path.startswith("/whoami"):
            return self.serve_whoami()
        if self.path.startswith("/where"):
            return self.serve_where()

        # 정적 파일(상대 경로만)
        rel = unquote(self.path.lstrip("/"))
        if ".." in rel or rel.startswith(("/", "\\")):
            return self.send_bytes(400, b"Bad Request", "text/plain; charset=utf-8")

        if os.path.isfile(rel):
            try:
                with open(rel, "rb") as f:
                    content = f.read()
                ctype, _ = mimetypes.guess_type(rel)
                return self.send_bytes(200, content, (ctype or "application/octet-stream"))
            except OSError:
                return self.send_bytes(500, b"Internal Server Error", "text/plain; charset=utf-8")

        return self.send_bytes(404, b"404 Not Found", "text/plain; charset=utf-8")

    # --- handlers ---
    def serve_index(self) -> None:
        if not os.path.exists(INDEX_FILE):
            return self.send_bytes(
                500,
                b"index.html not found (place index.html next to server.py)",
                "text/plain; charset=utf-8",
            )
        try:
            with open(INDEX_FILE, "rb") as f:
                self.send_bytes(200, f.read(), "text/html; charset=utf-8")
        except OSError:
            self.send_bytes(500, b"Internal Server Error", "text/plain; charset=utf-8")

    def serve_whoami(self) -> None:
        ip = client_ip(self)
        ok, geo = geolocate(ip)
        payload = {
            "time": now_str(),
            "ip": ip,
            "geo": geo if ok else {"error": geo.get("error"), "query": geo.get("query")},
        }
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_bytes(200, body, "application/json; charset=utf-8")

    def serve_where(self) -> None:
        ip = client_ip(self)
        ok, geo = geolocate(ip)
        if ok:
            html = (
                "<!doctype html><meta charset='utf-8'/>"
                "<h2>접속 정보</h2>"
                f"<p>시간: {now_str()}</p>"
                f"<p>IP: {ip}</p>"
                "<h3>대략적 위치</h3>"
                f"<ul>"
                f"<li>국가: {geo.get('country')}</li>"
                f"<li>지역: {geo.get('regionName')}</li>"
                f"<li>도시: {geo.get('city')}</li>"
                f"<li>좌표: {geo.get('lat')}, {geo.get('lon')}</li>"
                f"<li>시간대: {geo.get('timezone')}</li>"
                f"<li>ISP: {geo.get('isp')}</li>"
                f"</ul>"
            )
        else:
            html = (
                "<!doctype html><meta charset='utf-8'/>"
                "<h2>위치 조회 실패</h2>"
                f"<p>IP: {ip}</p>"
                f"<p>사유: {geo.get('error')}</p>"
            )
        self.send_bytes(200, html.encode("utf-8"), "text/html; charset=utf-8")


def run() -> None:
    httpd = HTTPServer((HOST, PORT), AppHandler)
    print(f"서버 시작: http://localhost:{PORT} (Ctrl+C 종료)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("서버 종료")


if __name__ == "__main__":
    run()
