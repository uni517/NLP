from loading_nemo import zh_spec_generator,vocoder#,en_spec_generator,en_quartznet,zh_quartznet,nmt_en_zh,nmt_zh_en
from convert_transcript import convert_transcript
#from interact import tokenizer, sample_sequence, model, hparams

import torch
import soundfile as sf
torch.cuda.empty_cache()
def ASR_EN(wavefile):
    en_text=''
    for i in en_quartznet.transcribe([wavefile]):
        en_text=i
    return(en_text)

def ASR_ZH(wavefile):
    zh_text=''
    for i in zh_quartznet.transcribe([wavefile]):
        zh_text=i
    return(zh_text)

def NMT_ZH_EN(zh_text):
    en_text = ''
    for i in nmt_zh_en.translate([zh_text], source_lang="zh", target_lang="en"):
        en_text = i
    return(en_text)

def NMT_EN_ZH(en_text):
    zh_text = nmt_en_zh.translate([en_text])
    return(zh_text)

def TTS_EN(en_text):
    parsed = en_spec_generator.parse(en_text)
    spectrogram = en_spec_generator.generate_spectrogram(tokens=parsed)
    audio = vocoder.convert_spectrogram_to_audio(spec=spectrogram)
    return audio
    #sf.write(filename, audio.to('cpu').detach().numpy()[0], 22050)


def TTS_ZH(zh_text):
    parsed = zh_spec_generator.parse(zh_text)
    spectrogram = zh_spec_generator.generate_spectrogram(tokens=parsed)
    audio = vocoder.convert_spectrogram_to_audio(spec=spectrogram)
    return audio
    #sf.write(filename, audio.to('cpu').detach().numpy()[0], 22050)

zh_text = convert_transcript("我喜歡在空閒時間閱讀")
a = TTS_ZH(zh_text)
sf.write("dialog_generate1_t1.wav", a.to('cpu').detach().numpy()[0], 22050)
zh_text = convert_transcript("我喜歡驚悚、懸疑、喜劇和愛情")
a = TTS_ZH(zh_text)
sf.write("dialog_generate1_t2.wav", a.to('cpu').detach().numpy()[0], 22050)


# def System_reply(history,personality):
#     history = history[-(2*hparams.max_history+1):]
#     #history.append(tokenizer.encode(input_text)) #tokenizer.encode編碼
    
#     personality = [tokenizer.encode(persona) for persona in personality]
    
#     history = [tokenizer.encode(text) for text in history]
#     with torch.no_grad(): #禁用梯度計算
#         output_ids = sample_sequence(personality, history, tokenizer, model, hparams)
    
#     output_text = tokenizer.decode(output_ids, skip_special_tokens=True)
#     return output_text