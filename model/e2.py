from six_Module import ASR_EN,ASR_ZH,NMT_ZH_EN,NMT_EN_ZH,TTS_EN,TTS_ZH,System_reply

def Chinese_to_English(remote_zhfile, remote_zh_text, enfilename):
    if remote_zhfile:
        remote_zh_text = ASR_ZH(remote_zhfile)

    en_text = NMT_ZH_EN(remote_zh_text)
    TTS_EN(enfilename, en_text)
    return remote_zh_text, en_text

def English_to_Chinese(local_enfilename, local_en_text):
    TTS_EN(local_enfilename, local_en_text)
    local_zh_text = NMT_EN_ZH(local_en_text)
    str2 = local_enfilename.split('.')
    str2 = int(str2[0])
    local_zhfilename = "local_zh"+str2
    TTS_ZH(local_zhfilename, local_zh_text)

def dialog(remote_enfile, remote_en_text, persona, history):
    if remote_enfile:
        remote_en_text = ASR_EN(remote_enfile)
    local_en_text = System_reply(history, persona, remote_en_text)
    English_to_Chinese(local_en_text)