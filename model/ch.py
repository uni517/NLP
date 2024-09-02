import nemo
import nemo.collections.asr as nemo_asr
import nemo.collections.nlp as nemo_nlp
import nemo.collections.tts as nemo_tts
import IPython
import soundfile as sf
import numpy


zh_spectrogram_generator = nemo_tts.models.Tacotron2Model.restore_from(restore_path="project/tacotron2_500/Tacotron2.nemo")
vocoder = nemo_tts.models.WaveGlowModel.from_pretrained(model_name="tts_waveglow_88m").cuda()

def TTS_ZH(zh_text):
    parsed = zh_spectrogram_generator.parse(zh_text) # 識別文字
    spectrogram = zh_spectrogram_generator.generate_spectrogram(tokens=parsed) # 轉成圖
    zh_audio =vocoder.convert_spectrogram_to_audio(spec=spectrogram) # 轉成聲碼
    for i in zh_audio:
        zh_audio = i
    return zh_audio



if __name__ == "__main__":

    audio = TTS_ZH("zhi4 yu2 shuo1 shou3 dou3 bu4 dou3 , zhe4 yu3 pai1 she4 zhe3 shi4 fou3 zhuan1 ye4 you3 guan1")
    sf.write("zh_speech_050.wav", audio.to('cpu').numpy(), 22050)