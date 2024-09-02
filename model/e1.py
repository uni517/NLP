#export PYTHONIOENCODING=utf-8
import string
import wave
import IPython
import random
import soundfile as sf
#from google_trans_new import google_translator
from itertools import chain
import nltk
#from model.interact import tokenizer
from model.six_Module import ASR_EN,ASR_ZH,NMT_ZH_EN,NMT_EN_ZH,TTS_EN,TTS_ZH#,System_reply

#translator = google_translator()

def speak_English(file):
    input_text = ASR_EN(file)
    print(input_text)
    return input_text

def speak_Chinese(file):
    zh_text = ASR_ZH(file)
    print('讀取的中文:',zh_text)
    en_text = NMT_ZH_EN(zh_text)
    print('翻譯成英文:',en_text)
    en_audio = TTS_EN(en_text)
    #sf.write("en_speech.wav", en_audio.to('cpu').numpy(), 22050)
    return zh_text, en_text, en_audio

def unlisten_English(en_text):
    zh_text = NMT_EN_ZH(en_text)
    print('路人甲(中文):',zh_text)
    zh_audio = TTS_ZH(zh_text)
    sf.write("zh_speech.wav", zh_audio.to('cpu').numpy(), 22050)

def unsee_English(en_text):
    re = ['!','?',',','.']
    for c in re:
        en_text = en_text.replace(c, "")
    en_text = en_text.strip().split()
    stopword = nltk.corpus.stopwords.words('english')
    # for en in en_text:
    #     if en not in stopword:
    #         print('英文:',en,' 中文:',translator.translate(en,lang_tgt='zh-tw'))
    

if __name__ == "__main__":
    history = []
    Language_English = True # True講英文 False講中文
    unlisten = True # True 聽不懂 False聽的懂
    unsee = True # True 看不懂 False看的懂
    zh_file = 'input_wav/Chinese/zh_01.wav' 
    en_file = 'input_wav/English/en_03.wav'
    # for key,value in select_persona.items():
    #     print(key,':',tokenizer.decode(chain(*value)))
    
    print('選擇的角色:', end='')
    name = input()
    personality = [[72, 1842, 6844, 764], [72, 1101, 3058, 2060, 475, 1312, 1101, 3492, 284, 285, 17697, 764], [72, 1842, 284, 711, 4652, 286, 24901, 764], [72, 1101, 257, 4708, 26713, 764]]
    while True:
        if Language_English:
            input_text = speak_English(en_file)
        else:
            print('不會說-----------------------')
            input_text = speak_Chinese(zh_file)
        
        input_text = input()
        print(input_text)
        output_text = System_reply(history, personality, input_text)
        print('路人甲:',output_text)
        output_audio = TTS_EN(output_text)
        sf.write("output_speech.wav", output_audio.to('cpu').numpy(), 22050)
        
        # if unlisten:
        #     print('聽不懂-----------------------')
        #     unlisten_English(output_text)

        # if unsee:
        #     print('看不懂-----------------------')
        #     unsee_English(output_text)
