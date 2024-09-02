from pypinyin import Style, lazy_pinyin

def is_chinese(_char):
    """
    Checks if a char is a Chinese character.
    """
    if not '\u4e00' <= _char <= '\u9fa5':
        return False
    return True


def replace_symbols(transcript):
    """
    Replaces Chinese symbols with English symbols.
    """
    transcript = transcript.replace("。", ".")
    transcript = transcript.replace("，", ",")
    transcript = transcript.replace("！", "!")
    transcript = transcript.replace("？", "?")
    return transcript

def convert_transcript(raw_trans):
    """
    Converts a Chinese transcript to a Chinese pinyin sequence.
    """
    symbols = ",.!?"
    # For simplicity, we only retain the Chinese chars and symbols
    trans = ''.join([_char for _char in replace_symbols(raw_trans) if is_chinese(_char) or _char in symbols])
    pinyin_trans = []
    for pinyin in lazy_pinyin(trans, style=Style.TONE3):
        if pinyin not in symbols and not pinyin[-1].isdigit():
            pinyin_trans.append(pinyin + "0")
        else:
            pinyin_trans.append(pinyin)
    return " ".join(pinyin_trans)    


# if __name__ == "__main__":

#     text = '我的愛好是談吉他'
#     text_2 = convert_transcript(text)
#     print(text,text_2)
