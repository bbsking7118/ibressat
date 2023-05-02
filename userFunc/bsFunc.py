
def change_amt_format(data, percent):  # 금액을 천단위 콤마(",")를 추가하여 반환하는 함수
    is_minus = False  # 마이너스 표기를 거짓으로 지정
    if data.startswith('-'):  # 입력된 금액의 앞자리가 - 일 경우
        is_minus = True  # 마이너스 표기를 참으로 지정
    strip_str = data.lstrip('-0')  # 입력된 금액의 앞자리에 - 기호나 0을 삭제하여 반환
    if strip_str == '':  # 입력된 금액이 공백이라면
        if percent == 1:  # 퍼센트 구분 기호가 1이라면
            return '0.00'  # 0.00 으로 반환
        else:  # 퍼센트 구분 기호가 1이 아니라면
            return '0'  # 0 으로 반환
    if percent == 1:  # 퍼센트 구분 기호가 1이라면
        strip_data = int(strip_str)  # 입력값을 int로 변환 후
        strip_data = strip_data / 100  # 100으로 나눠주고
        form = format(strip_data, ',.2f')  # 소수점 2자리까지 자름
    elif percent == 2:  # 퍼센트 구분 기호가 2이라면
        strip_data = float(strip_str)  # 입력값을 float로 변환 후
        form = format(strip_data, ',.2f')  # 소수점 2자리까지 자름
    else:  # 퍼센트 구분 기호가 1 또는 2가 아니라면
        strip_data = int(strip_str)  # 입력값을 int로 변환 후
        form = format(strip_data, ',d')  # 정수형으로 만듬
    if form.startswith('.'):  # 변환된 금액의 앞자리가 . 으로 시작한다면
        form = '0' + form  # 변환된 금액에 앞에 0을 붙여줌
    if is_minus:  # 입력된 금액이 마이너스 였다면
        form = '-' + form  # 변환된 금액에 앞에 - 기호를 붙여줌
    return form  # 변환됨 금액을 반환함
