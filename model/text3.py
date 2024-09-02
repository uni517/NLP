from six_Module import NMT_EN_ZH,TTS_ZH
from translate import Translator
from convert_transcript import convert_transcript

stopword = ['i','hi', 'me','yes','no', 'my', 'myself', 'we', 'our', 'ours','get', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
translator= Translator(to_lang="chinese")

def English_to_Chinese(local_en_text):
    local_zh_text = NMT_EN_ZH(local_en_text)[0]
    local_en_text = local_en_text.lower()
    re = ['!','?',',','.','。']
    for c in re:
        local_en_text = local_en_text.replace(c, "")

    text = local_en_text.split(' ')
    en_text = ''
    for i in text:
        if i not in stopword:
            #en = NMT_EN_ZH(i)
            print(i)
            en = translator.translate(i)
            en_text += i + " " + en+'; '
    zh_text = convert_transcript(local_zh_text)
    audio = TTS_ZH(zh_text)
    return local_zh_text, en_text, audio