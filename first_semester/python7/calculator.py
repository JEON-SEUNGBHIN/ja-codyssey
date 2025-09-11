from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

# 계산기 동작 처리 클래스
class Calculator:
    def __init__(self):
        self.reset()

    # 초기 상태로 리셋
    def reset(self):
        self.current = ''
        self.display_value = ''
        self.operand = None
        self.operator = None
        self.result = None
        self.new_input = True
        self.after_equal = False

    # 각 연산자 버튼 처리 함수
    def add(self): self._calculate('+', '+')
    def subtract(self): self._calculate('-', '−')
    def multiply(self): self._calculate('*', '×')
    def divide(self): self._calculate('/', '÷')

    # 퍼센트 계산 처리
    def percent(self):
        try:
            if not self.current or self.current == '-':
                return
            current_val = float(self.current)
            op = self.operator
            if self.operand is not None and op in ['+', '-', '*', '/']:
                
                # 덧셈, 뺄셈은 기준값(operand) 대비 백분율
                if op in ['+', '-']:
                    percent_val = self.operand * current_val / 100
                else:
                    percent_val = current_val / 100
            else:
                percent_val = current_val / 100
            self.current = str(percent_val)
            self.display_value += '%'
            self.new_input = True
        except:
            self.current = 'Error'
            self.display_value = 'Error'

    # ± 버튼 눌렀을 때 부호 변경 처리
    def negative_positive(self):
        if self.after_equal:
            self.reset()

        if not self.current:
            self.current = '-'
            self.display_value += '-'
            return

        if self.current == '-':
            self.current = ''
            self.display_value = self.display_value[:-1]
            return

        # 현재 숫자 앞에 - 붙이거나 제거
        if self.current.startswith('-'):
            self.current = self.current[1:]
        else:
            self.current = '-' + self.current

        # 화면에 표시된 수식도 함께 수정
        tokens = self.display_value.strip().split(' ')
        if tokens:
            last = tokens[-1]
            if last.endswith('%'):
                return
            if last.replace('.', '', 1).lstrip('-').isdigit():
                tokens[-1] = self.current
                self.display_value = ' '.join(tokens)

    # 숫자 입력 처리
    def input_digit(self, digit):
        if self.after_equal:
            self.reset()

        if self.new_input:
            if self.current == '-':
                self.current += digit
                self.display_value += digit
                self.new_input = False
            else:
                self.current = digit
                self.display_value += digit
                self.new_input = False
        else:
            self.current += digit
            self.display_value += digit

    # 소수점 입력 처리
    def input_dot(self):
        if '.' not in self.current:
            if self.current == '':
                self.current = '0.'
                self.display_value += '0.'
            else:
                self.current += '.'
                self.display_value += '.'

    # 연산자 버튼 처리
    def _calculate(self, op_internal, op_display):
        if self.after_equal:
            self.after_equal = False

        # 수식 처음에 음수 입력 허용
        if self.display_value == '' and op_internal == '-':
            self.current = '-'
            self.display_value = '-'
            return

        # 연산자 중복 입력 시 교체
        tokens = self.display_value.strip().split(' ')
        if tokens and tokens[-1] in ['+', '−', '×', '÷']:
            tokens[-1] = op_display
            self.display_value = ' '.join(tokens)
            self.operator = op_internal
            return

        if not self.current or self.current == '-':
            return

        try:
            self.operand = float(self.current)
        except:
            self.current = 'Error'
            self.display_value = 'Error'
            return

        self.operator = op_internal
        self.display_value += f' {op_display} '
        self.new_input = True

    # = 버튼 처리
    def equal(self):
        if self.operator is None or self.operand is None or self.current in ['', '-']:
            return
        try:
            right = float(self.current)
            if self.operator == '+':
                self.result = self.operand + right
            elif self.operator == '-':
                self.result = self.operand - right
            elif self.operator == '*':
                self.result = self.operand * right
            elif self.operator == '/':
                if right == 0:
                    raise ZeroDivisionError
                self.result = self.operand / right
            if abs(self.result) > 1e100:
                raise OverflowError("Result too large")
        except (ZeroDivisionError, OverflowError, ValueError):
            self.current = 'Error'
            self.display_value = 'Error'
        else:
            self.current = self._format_result(self.result)
            self.display_value = self.current
        self.operator = None
        self.operand = None
        self.new_input = True
        self.after_equal = True

    # 결과 포맷 처리
    def _format_result(self, result):
        return str(int(result)) if result.is_integer() else f"{result:.6g}"

    def get_display(self):
        return self.display_value

# UI 구성 클래스
class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iOS Style Calculator")
        self.calculator = Calculator()
        self.setStyleSheet("background-color: #000000;")
        self.init_ui()

    def init_ui(self):
        self.display = QLabel(self.calculator.get_display())
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet("color: white; font-size: 50px; background: black; padding: 20px;")
        grid = QGridLayout()
        grid.setSpacing(10)

        # 버튼 배치 정의
        button_map = [
          [('AC', self.calculator.reset, '#d4d4d2', 'black'),
            ('+/-', self.calculator.negative_positive, '#d4d4d2', 'black'),
            ('%', self.calculator.percent, '#d4d4d2', 'black'),
            ('÷', self.calculator.divide, '#ff9500', 'white')],
          [('7', lambda: self.calculator.input_digit('7'), '#505050', 'white'),
            ('8', lambda: self.calculator.input_digit('8'), '#505050', 'white'),
            ('9', lambda: self.calculator.input_digit('9'), '#505050', 'white'),
            ('×', self.calculator.multiply, '#ff9500', 'white')],
          [('4', lambda: self.calculator.input_digit('4'), '#505050', 'white'),
            ('5', lambda: self.calculator.input_digit('5'), '#505050', 'white'),
            ('6', lambda: self.calculator.input_digit('6'), '#505050', 'white'),
            ('−', self.calculator.subtract, '#ff9500', 'white')],
          [('1', lambda: self.calculator.input_digit('1'), '#505050', 'white'),
            ('2', lambda: self.calculator.input_digit('2'), '#505050', 'white'),
            ('3', lambda: self.calculator.input_digit('3'), '#505050', 'white'),
            ('+', self.calculator.add, '#ff9500', 'white')],
          [('0', lambda: self.calculator.input_digit('0'), '#505050', 'white'),
            ('.', self.calculator.input_dot, '#505050', 'white'),
            ('=', self.calculator.equal, '#ff9500', 'white')]
        ]

        # 버튼 생성 및 배치
        for row, line in enumerate(button_map):
            col = 0
            for text, handler, bg_color, fg_color in line:
                btn = QPushButton(text)
                btn.setStyleSheet(f"background-color: {bg_color}; color: {fg_color}; font-size: 24px; border: none; border-radius: 30px;")
                if text == '0':
                    btn.setFixedHeight(60)
                    btn.setFixedWidth(160)
                    grid.addWidget(btn, row + 1, col, 1, 2)
                    col += 2
                else:
                    btn.setFixedSize(80, 60)
                    grid.addWidget(btn, row + 1, col)
                    col += 1
                btn.clicked.connect(lambda _, h=handler: self.button_clicked(h))

        vbox = QVBoxLayout()
        vbox.addWidget(self.display)
        vbox.addLayout(grid)
        self.setLayout(vbox)

    # 버튼 클릭 시 디스플레이 업데이트
    def button_clicked(self, handler):
        handler()
        self.display.setText(self.calculator.get_display())
        length = len(self.calculator.get_display().replace(",", ""))
        font_size = 50 if length <= 6 else 40 if length <= 12 else 30
        self.display.setStyleSheet(f"color: white; font-size: {font_size}px; background: black; padding: 20px;")

# 프로그램 실행
if __name__ == "__main__":
    app = QApplication([])
    calc_ui = CalculatorUI()
    calc_ui.show()
    app.exec_()
