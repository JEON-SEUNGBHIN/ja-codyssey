import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
)
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iOS 스타일 계산기")
        self.setFixedSize(400, 600)  # 고정된 창 크기 설정
        self._create_ui()  # UI 생성 함수 호출

    def _create_ui(self):
        # 전체 세로 레이아웃 생성
        main_layout = QVBoxLayout()

        # 상단 출력창 설정
        self.display = QLabel('0')  # 처음엔 0으로 시작
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 오른쪽 정렬
        self.display.setStyleSheet("""
            background-color: black;
            color: white;
            font-size: 48px;
            padding: 30px 20px;
        """)
        main_layout.addWidget(self.display)

        # 버튼 정의 (텍스트, 스타일키)
        buttons = [
            [('AC', 'light'), ('±', 'light'), ('%', 'light'), ('÷', 'orange')],
            [('7', 'dark'), ('8', 'dark'), ('9', 'dark'), ('×', 'orange')],
            [('4', 'dark'), ('5', 'dark'), ('6', 'dark'), ('-', 'orange')],
            [('1', 'dark'), ('2', 'dark'), ('3', 'dark'), ('+', 'orange')],
            [('0', 'dark'), ('.', 'dark'), ('=', 'orange')],
        ]

        # 버튼 그리드 레이아웃 생성
        grid_layout = QGridLayout()
        for row, row_buttons in enumerate(buttons):
            col_offset = 0  # '0' 버튼이 두 칸을 차지할 때 이후 버튼을 밀기 위해 사용
            for col, (text, color) in enumerate(row_buttons):
                button = QPushButton(text)

                if text == '0':
                    # 0 버튼은 넓은 타원형으로 만들기
                    button.setFixedHeight(80)
                    button.setMinimumWidth(160)  # 두 칸에 걸쳐 배치
                    button.setStyleSheet("""
                        font-size: 24px;
                        background-color: #505050;
                        color: white;
                        border-radius: 40px;
                        padding-left: 24px;
                        text-align: left;
                    """)
                    grid_layout.addWidget(button, row, col, 1, 2)  # 두 칸 차지
                    col_offset += 1  # 다음 버튼 한 칸 밀기
                else:
                    # 일반 버튼 (정사각형 원형)
                    button.setFixedSize(80, 80)
                    button.setStyleSheet(self._get_button_style(color, text))
                    grid_layout.addWidget(button, row, col + col_offset)

                # 버튼 클릭 시 실행될 함수 연결
                button.clicked.connect(lambda checked, t=text: self._on_click(t))

        # 레이아웃을 메인 레이아웃에 추가
        main_layout.addLayout(grid_layout)
        self.setLayout(main_layout)

    def _get_button_style(self, color, text):
        """버튼 색상과 공통 스타일 설정"""
        styles = {
            'dark': "background-color: #505050; color: white;",     # 숫자 버튼
            'light': "background-color: #D4D4D2; color: black;",     # AC, ±, %
            'orange': "background-color: #FF9500; color: white;"     # 연산자
        }
        return f"""
            border-radius: 40px;
            font-size: 24px;
            {styles[color]}
        """

    def _on_click(self, text):
        """버튼 클릭 이벤트 처리 함수"""
        current = self.display.text()

        if text == 'AC':
            self.display.setText('0')  # 전체 초기화
        elif text == 'C':
            self.display.setText(current[:-1] if len(current) > 1 else '0')  # 한 자리 지움
        elif text == '=':
            try:
                # 연산자 문자 변환 후 계산
                expression = current.replace('×', '*').replace('÷', '/')
                result = eval(expression)
                self.display.setText(str(result))
            except:
                self.display.setText('Error')  # 계산 실패 시
        elif text == '±':
            # 부호 반전
            try:
                if current.startswith('-'):
                    self.display.setText(current[1:])
                else:
                    self.display.setText('-' + current)
            except:
                self.display.setText('Error')
        elif text == '%':
            # 백분율 처리
            try:
                self.display.setText(str(float(current) / 100))
            except:
                self.display.setText('Error')
        else:
            # 일반 숫자나 연산자 입력
            if current == '0' and text not in ['+', '-', '×', '÷', '.']:
                self.display.setText(text)  # 처음 입력이면 덮어쓰기
            else:
                self.display.setText(current + text)  # 이어 붙이기


# 앱 실행부
if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())
