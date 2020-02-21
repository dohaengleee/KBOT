import re

chosung_list = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ" ]
jungsung_list = ["ㅏ","ㅐ","ㅑ","ㅒ","ㅓ","ㅔ","ㅕ","ㅖ","ㅗ","ㅘ","ㅛ","ㅙ","ㅚ","ㅜ","ㅝ","ㅞ","ㅟ","ㅠ","ㅡ","ㅢ","ㅣ"]
jongsung_list = [" ","ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ","ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ","ㅁ","ㅂ","ㅄ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]

#0 1 2 3 4 5 6 7 8 9
digit_list = [True, True, False, True, False, False, True, True, True, False]

# 0 ~ 9 숫자의 로/으로 처리
digit_ro_list = [True, False, False, True, False, False, True, False, False, False]

#a b c d e f g h i j k l m n o p q r s t u v w x y z
alphabet_list = [False, True, True, True, False, False, False, False, False, False, True, True, True, True, False, True, True, False, False, True, False, False, False, False, False, False]
alphabet_alone_list = [False, False, False, False, False, False, False, False, False, False, False, True, True, True, False, False, False, True, False, False, False, False, False, False, False, False]

def make_sentence(frame,condition):
    #### 조사 처리
    i=0
    position=[]
    for m in re.finditer('post', frame):
        i=i+1
        position.append([m.start(), m.end()])
    
    if i>0:
        frame_copy=frame
        num=len(condition)
        posts=[]
        for pos in position:
            p=pos[0]
            if frame_copy[p-3]=="%":p=p-6
            index=int(find_number(frame_copy,p-2))
            
             
            post="이" if has_jongsung(condition[index]) else "가"
            
            posts.append(post)
            frame=str(frame.replace("post",str(num),1))
            num+=1            
        
        for pos in posts:
            condition.append(pos)

#### 조사 처리
    i=0
    position=[]
    for m in re.finditer('pposi', frame):
        i=i+1
        position.append([m.start(), m.end()])
    
    if i > 0:
        frame_copy = frame
        num = len(condition)
        posts = []
        for pos in position:
            p = pos[0]
            if frame_copy[p-3] == "%":
                p = p-6
            index = int(find_number(frame_copy, p-2))
            
            post = "은" if has_jongsung(condition[index]) else "는"
            
            posts.append(post)
            frame = str(frame.replace("pposi", str(num), 1))
            num += 1
        
        for pos in posts:
            condition.append(pos)
            
    sentence = frame.format(*condition)

    return sentence


def find_number(s, p):

    i = 0
    num = ''
    while True:
        if is_number(s[p-i]):
            num += s[p-i]
        else:
            if s[p-i] == "{":
                return num[::-1]
        i = i+1


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False  


def has_jongsung(word):
    #공백일 경우 처리
    if word == "":
        return ""

    word_up = word.upper()
    target_list = []
    brace = []
    brace_count = 0

    for idx, s_str in enumerate(word_up):
        if s_str == '(':
            brace_count += 1
        brace.append(s_str)

        if s_str == '#':
            index = idx
            l_str = word_up[index - 1]
            c_str = word_up[index + 1]
            if l_str == ')':
                for i in range(brace_count):
                    while brace.pop() != '(':
                        pass
                brace_count = 0
                l_str = brace[-1]
                brace = []
            target_list.append(l_str)

        for target_char in target_list:

            uni = ord(target_char)

            if target_char == ' ':
                return False

            offset = ord(u'0')
            if uni >= offset and uni < offset + 10:
                if c_str == '으로' or c_str == '로':
                    return digit_ro_list[ (uni-offset) ]
                return digit_list[ (uni-offset) ]

            offset = ord(u'A')
            if uni >= offset and uni < offset + 26:
                return alphabet_alone_list[ (uni-offset) ]

            offset = ord(u"가")
            jongsung = jongsung_list[ (uni-offset) % len(jongsung_list) ]
            if c_str == '으' or c_str == '로' and jongsung == 'ㄹ':
                return False
            if jongsung == " ":
                return False
            else:
                return True


def get_josa(text):

    result = text

    # false_dict = {'은': '는', '이': '가', '로': '으로', '을': '를', '과': '와'}

    for i, s_str in enumerate(result):
        if s_str == '#':
            index = result.index(s_str)
            l_str = result[index - 1]
            c_str = result[index + 1]

            _decn = has_jongsung(result)

            if c_str == '은' or c_str == '는':
                if _decn:
                    change_words = '은'
                else:
                    change_words = '는'

            if c_str == '이' or c_str == '가':
                if _decn:
                    change_words = '이'
                else:
                    change_words = '가'

            if c_str == '으' or c_str == '로':
                if _decn:
                    change_words = '으로'
                else:
                    change_words = '로'

            if c_str == '을' or c_str == '를':
                if _decn:
                    change_words = '을'
                else:
                    change_words = '를'

            if c_str == '과' or c_str == '와':
                if _decn:
                    change_words = '과'
                else:
                    change_words = '와'

            if result[index + 1: index + 3] == '으로':
                temp = result[index + 3]
                result = "".join((result[:index], change_words, temp, result[index + 3:]))

            result = "".join((result[:index], change_words, result[index + 2:]))

    return result
