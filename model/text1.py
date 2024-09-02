from model.six_Module import ASR_ZH, TTS_EN, NMT_ZH_EN
import soundfile as sf
from googletrans import Translator

translator = Translator()

def speak_Chinese(file):
    zh_text = ASR_ZH(file)
    en_text = NMT_ZH_EN(zh_text)
    #en_audio = TTS_EN(en_text)

    
    print('讀取的中文:',zh_text)
    print('翻譯成英文:',en_text)
    #sf.write("en_speech.wav", en_audio.to('cpu').numpy(), 22050)
    return zh_text, en_text#, en_audio