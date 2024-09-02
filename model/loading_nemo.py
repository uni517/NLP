# import nemo.collections.asr as nemo_asr
# import nemo.collections.nlp as nemo_nlp
from nemo.collections.tts.models.base import SpectrogramGenerator, Vocoder
from nemo.collections.nlp.models import MTEncDecModel
#ASR #https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/stable/asr/results.html#ngc-pretrained-checkpoints
# en_quartznet = nemo_asr.models.EncDecCTCModel.restore_from(restore_path="/home/ailab/0902project/lightning-compac/nemo_models/ASR/stt_en_quartznet15x5.nemo").cuda()
# zh_quartznet = nemo_asr.models.EncDecCTCModel.restore_from(restore_path="/home/ailab/0902project/lightning-compac/nemo_models/ASR/stt_zh_quartznet15x5.nemo").cuda()

# #NMT #https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/v1.0.0/nlp/machine_translation.html
# # nmt_zh_en = nemo_nlp.models.MTEncDecModel.restore_from(restore_path="/home/ailab/0902project/lightning-compac/nemo_models/NMT/nmt_zh_en_transformer6x6.nemo").cuda() #中翻英
# nmt_en_zh = nemo_nlp.models.MTEncDecModel.restore_from(restore_path="/home/ailab/0902project/lightning-compac/nemo_models/NMT/nmt_en_zh_transformer6x6.nemo").cuda() #英翻中
#nmt_zh_en  = nemo_nlp.models.machine_translation.MTEncDecModel.from_pretrained(model_name="nmt_zh_en_transformer6x6")

nmt_zh_en = MTEncDecModel.from_pretrained("nmt_zh_en_transformer6x6").cuda()

#TTS #https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/stable/tts/intro.html
zh_spec_generator = SpectrogramGenerator.restore_from(restore_path="/home/ailab/0902project/lightning-compac/nemo_models/TTS/tts_zh_fastpitch.nemo").cuda()
en_spec_generator = SpectrogramGenerator.restore_from(restore_path="/home/ailab/0902project/lightning-compac/nemo_models/TTS/tts_en_fastpitch.nemo").cuda()
vocoder = Vocoder.restore_from(restore_path="/home/ailab/0902project/lightning-compac/nemo_models/TTS/tts_hifigan.nemo").cuda()
