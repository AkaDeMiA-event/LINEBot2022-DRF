# from django.http import HttpResponse
# from .request_create import LineMessage, create_text_message
import base64
import hashlib
import hmac

from .bot_info import channel_secret


def can_convert_to_uint(message_text):
    try:
        # 文字列を実際にint関数で変換してみる
        number = int(message_text, 10)
    except ValueError:
        # 例外が発生＝変換できないのでFalseを返す
        return False
    if not number > 0:
        return False
    return True


def has_same_numbers(num_array):
    return len(num_array) != len(set(num_array))


# line_botからの入力をvalidateしてOKなら配列を返す関数を定義　単体テストずみ
def validate_or_process_message(message_text):
    # 数字に変換可能か。
    if not can_convert_to_uint(message_text):
        return False
    number = int(message_text)
    if number > 0:
        # numberは正の整数 message_textは数値変換可能なもの
        if len(message_text) == 4:
            list_str = list(message_text)
            # 1文字ずつに分離して数字に
            list_num = [int(s) for s in list_str]
            if not has_same_numbers(list_num):
                return list_num


def validate_numeron_numbers(numbers, digits):
    return len(numbers) == digits and not has_same_numbers(numbers)


def validate_line_signature(request):
    body = request.body.decode("utf-8")
    hash_value = hmac.new(
        channel_secret.encode("utf-8"), body.encode("utf-8"), hashlib.sha256
    ).digest()
    signature = base64.b64encode(hash_value)
    return request.META.get("HTTP_X_LINE_SIGNATURE").encode("utf-8") == signature


def message_is_text(message):
    return message["type"] == "text"
