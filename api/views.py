import json
import random

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Numeron
from .request_create import LineMessage, create_text_message
from .validators import (
    can_convert_to_uint,
    message_is_text,
    validate_line_signature,
    validate_numeron_numbers,
)


class EcholaliaView(APIView):
    def post(self, request):
        if not validate_line_signature(request):
            return Response("Requests msut be sent from LINE", status=status.HTTP_400_BAD_REQUEST)
        # lineのエンドポイントにおくるリクエストに必要なもの定義
        request_json = json.loads(request.body.decode("utf-8"))
        events = request_json["events"]
        if not events:
            return Response("LINE Developer Verification", status=status.HTTP_200_OK)
        data = events[0]
        message = data["message"]
        reply_token = data["replyToken"]

        # スタンプやメディア系をバリデーション
        if not message_is_text(message):
            line_message = LineMessage(create_text_message("不正な入力です。"))
            line_message.reply(reply_token)
            return Response("Messages msut be text", status=status.HTTP_400_BAD_REQUEST)

        message_text = message["text"]
        # おうむ返しのコード
        # message_textの部分をいじれば好きな文言に変えることができる。
        line_message = LineMessage(create_text_message(message_text))
        line_message.reply(reply_token)
        return Response("", status=status.HTTP_200_OK)


class NumeronView(APIView):
    def post(self, request):
        if not validate_line_signature(request):
            return Response("Requests msut be sent from LINE", status=status.HTTP_400_BAD_REQUEST)

        # lineのエンドポイントにおくるリクエストに必要なもの定義
        request_json = json.loads(request.body.decode("utf-8"))
        events = request_json["events"]
        if not events:
            return Response("LINE Developer Verification", status=status.HTTP_200_OK)

        data = events[0]
        message = data["message"]
        reply_token = data["replyToken"]
        user_id = data["source"]["userId"]

        # スタンプやメディア系をバリデーション
        if not message_is_text(message):
            reply_to_invalid_message(reply_token)
            return Response("Messages msut be text", status=status.HTTP_400_BAD_REQUEST)

        message_text = message["text"]

        my_data = Numeron.objects.filter(line_id=user_id)
        if message_text == "start":
            # データベースに一つの値だけにしたい。

            if my_data.exists():
                my_data.delete()
                line_message = LineMessage(create_text_message("ゲームがリスタートしました。4桁の数字を入力してください。"))
            else:
                line_message = LineMessage(create_text_message("ゲームがスタートしました。4桁の数字を入力してください。"))

            # ランダムに数字を生成 重複なしの４つの数字
            random_number_array = random.sample(range(0, 10), k=4)
            target_num_str = "".join(map(str, random_number_array))
            Numeron.objects.create(number_str=target_num_str, line_id=user_id)
            line_message.reply(reply_token)
            return Response("Answer data is created", status=status.HTTP_201_CREATED)

        elif message_text == "stop":
            if my_data.exists():
                my_data.delete()
                line_message = LineMessage(create_text_message("ゲームが終了しました。"))
                line_message.reply(reply_token)
                return Response("This game is successfuly terminated", status=status.HTTP_200_OK)
            line_message = LineMessage(create_text_message("ゲームが始まっていません。"))
            line_message.reply(reply_token)
            return Response("The game has not been started", status=status.HTTP_200_OK)

        if not my_data.exists():
            reply_to_invalid_message(reply_token)
            return Response("Invalid Message", status=status.HTTP_400_BAD_REQUEST)

        if not can_convert_to_uint(message_text):
            reply_to_invalid_message(reply_token)
            return Response("Invalid Message", status=status.HTTP_400_BAD_REQUEST)

        number_strs = list(message_text)
        numbers = [int(s) for s in number_strs]
        if not validate_numeron_numbers(numbers, 4):
            reply_to_invalid_message(reply_token)
            return Response("Invalid Message", status=status.HTTP_400_BAD_REQUEST)

        try:
            answer_str = Numeron.objects.get(line_id=user_id).number_str
        except Exception as e:
            line_message = LineMessage(create_text_message(f"データベースに異常があります。\n{str(e)}"))
            line_message.reply(reply_token)
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 比較対象の配列
        answer_numbers = [int(s) for s in list(answer_str)]
        # ただしく動いている
        # この部分を書かせたい。
        eat, bite = my_numeron(numbers, answer_numbers)
        reply_message = f"{eat}EAT-{bite}BITE"
        if eat == 4:
            reply_message += "\nゲームクリア！！！\nおめでとう！！！"
            my_data.delete()
        line_message = LineMessage(create_text_message(reply_message))
        line_message.reply(reply_token)
        return Response("", status=status.HTTP_200_OK)


# TODO: こちらを実装してみましょう
def my_numeron(input_numbers, answer_numbers):
    eat = 0
    bite = 0
    for i, number in enumerate(input_numbers):
        if number in answer_numbers:
            if number == answer_numbers[i]:
                eat += 1
            else:
                bite += 1
    return eat, bite


def reply_to_invalid_message(reply_token):
    line_message = LineMessage(create_text_message("不正な入力です。"))
    line_message.reply(reply_token)
