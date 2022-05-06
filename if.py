def main(a):
    # aの値は整数しか入れない想定
    if a <= 8:
        print("aは8以下です")
    elif a > 20:
        print("aは20より大きいです")
    elif a >= 9 and a < 19:
        print("aは9以上で19未満です")
    else:
        print("aは19です。")


main(8)
