from six_Module import ASR_EN,ASR_ZH,NMT_ZH_EN,NMT_EN_ZH,TTS_EN,TTS_ZH,System_reply

def dialog(persona, history):
    local_en_text = System_reply(history, persona)
    audio = TTS_EN(local_en_text)
    return local_en_text, audio