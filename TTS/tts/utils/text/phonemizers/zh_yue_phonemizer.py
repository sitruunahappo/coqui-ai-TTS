from typing import Any

from TTS.tts.utils.text.cantonese.phonemizer import text2phonemes
from TTS.tts.utils.text.phonemizers.base import BasePhonemizer


# Some weird punctuations found on the dataset used
_DEF_PUNCS = '，﹐。？！、：；“”‘’／‧・～＋☓＝⋯丶＊＃（）「」『』《》［］'


class ZH_YUE_Phonemizer(BasePhonemizer): 
    language = 'zh-yue'

    def __init__(self, 
                 punctuations: str = _DEF_PUNCS, 
                 keep_puncs: bool = True, 
                 **kwargs: Any):
        super().__init__(self.language, 
                         punctuations=punctuations, 
                         keep_puncs=keep_puncs)

    @staticmethod
    def name():
        return 'zh_yue_phonemizer'

    @staticmethod
    def supported_languages() -> dict:
        return {'zh-yue': 'Cantonese'}

    def _phonemize(self, text: str, separator:bool, ipa: bool, tone_letters: bool) -> str:
        return text2phonemes(text, 
                             sep=separator, 
                             ipa=ipa, 
                             tone_letters=tone_letters)

    def phonemize(self, 
                  text, 
                  separator: str = '|', 
                  ipa: bool = True, 
                  tone_letters: bool = False,
                  language: str | None = None) -> str:
        return self._phonemize(text, separator, ipa, tone_letters)

    def is_supported_languages(self) -> bool:
        return True

    def version(self) -> str:
        return '0.0.1'

    def is_available(self) -> bool:
        return True


'''
if __name__ == '__main__':
    text_1 = '香港人講廣東話。' 
    text_2 = '仲所以咩？用粵拼啦！'

    e = ZH_YUE_Phomenizer()
    print(e.supported_languages())
    print(e.version())
    print(e.language)
    print(e.name())
    print(e.is_available())
    
    print("`" + e.phonemize(text_1) + "`")
'''
