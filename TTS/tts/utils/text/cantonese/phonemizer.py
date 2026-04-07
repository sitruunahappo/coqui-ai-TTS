import pycantonese

from .jyutping2ipa import INIT_DICT, CODA_DICT, TONE_DICT, ENTERING_TONES, TONE_LETTERS


def _jyutping2ipa(components: pycantonese.jyutping.Jyutping, 
                  sep: str, 
                  tone_letters: bool) -> str:
    '''Swap Jyutping with IPA symbol

    For the scheme itself, check https://jyutping.org/en/jyutping/
    For IPA, check the dotstring of the dictionary file

    Using the Jyutping scheme, the output might be different with the API 
    provided by pycantonese
    '''

    varieties = ('ing', 'ik', 
                 'ung', 'uk', 
                 'ei', 'ou')
    enterings = ('t', 'p', 'k')

    # bool is basically int but more beautiful (~~I like C~~)
    i = int(components.final in varieties)

    onset = INIT_DICT.get(components.onset, [''])[0]
    nucleus = INIT_DICT.get(components.nucleus, [''])[i]
    coda = CODA_DICT.get(components.coda, '')

    if tone_letters:
        tone = TONE_LETTERS.get(components.tone, '')
    else:
        if components.coda in enterings:
            tone = ENTERING_TONES.get(components.tone, '')
        else:
            tone = TONE_DICT.get(components.tone, '')

    # Filter out empty part and concatenate to a str
    ipa_components = list(filter(None, [onset, nucleus, coda, tone]))
    return sep.join(ipa_components)


def _parse_jyutping(jyutping: str, 
                    ipa: bool, 
                    sep: str, 
                    tone_letters: bool) -> list[str]:
    '''Parse word-segmented jyutping string
    
    The romanistion from characters_to_jyutping() is word-segmented, 
    so an extra parsing is needed to make it map to each character.

    For example:
        'hoeng1gong2jan4' -> ['hoeng1', 'gong2', 'jan4']
        (or IPA version)
        (or add `sep` to each components)
    '''
    
    parsed = pycantonese.parse_jyutping(jyutping)
    flat_jyutping = []
    for components in parsed:
        if ipa:
            parsed_jyutping = _jyutping2ipa(components, 
                                            sep=sep, 
                                            tone_letters=tone_letters)
        else:
            components_lst = list(filter(None, [components.onset, 
                                                components.nucleus, 
                                                components.coda, 
                                                components.tone]))
            parsed_jyutping = sep.join(components_lst)
        
        flat_jyutping.append(parsed_jyutping)

    return flat_jyutping


def _text2phonemes(text: str, **kwargs) -> list[str]:
    '''Parse the whole text to phonemes level
    
    The characters_to_jyutping() can take a whole string and output the 
    word-segmented Jyutping, so it needs some steps to parse 
    
    For example:
        '香港人講廣東話' 
        -> [('香港人', 'hoeng1gong2jan4'), ('講', 'gong2'), 
            ('廣東話', 'gwong2dung1waa2')]
        -> ['hoeng1', 'gong2', 'jan4', 'gong2', 
            'gwong2', 'dung1', 'waa2'] (The true output)
    '''

    char_jyutping = pycantonese.characters_to_jyutping(text)
    
    plain_jyutping = []

    # TODO: Spaghetti code, refactoring later
    for char, jyutping in char_jyutping:
        if jyutping is None:
            '''
            Due to the design of PyCantonese parser, it is possible that 
            the `None` means that it is a phrase unknown to its corpus. 
            Consider the example below:
            
                > pycantonese.characters_to_jyutping('架車搶軚，要去調返啱個軚尺。')
                > [('架車搶軚，要', None),
                   ('去', 'heoi3'),
                   ('調', 'tiu4'),
                   ('返', 'faan2'),
                   ('啱個', 'ngaam1go3'),
                   ('軚尺', 'taai5cek3'),
                   ('。', None)]
            
            Currently the solution is to separate each character and 
            parse again. If the output is still `None`, then it should be 
            a real unknown char, or a punctuation.
            '''
            
            if len(char) == 1:
                # It makes no sense to handle a single char
                plain_jyutping.append(char)
            else:
                # Simple reparse
                # NOTE: Perhaps a better variable name?
                eval_phrase = (pycantonese.characters_to_jyutping(c) 
                               for c in char)

                for eval_item in eval_phrase:
                    for eval_char, eval_jyutping in eval_item:
                        if eval_jyutping is None:
                            plain_jyutping.append(eval_char)
                        else:
                            plain_jyutping.extend(_parse_jyutping(eval_jyutping,
                                                                  **kwargs)) 
        else:
            plain_jyutping.extend(_parse_jyutping(jyutping, **kwargs))

    return plain_jyutping


def text2phonemes(text: str, sep='|', ipa=False, tone_letters=False) -> str:
    # tips: one can always parse words with something like r'.+\d+' (chars + tones)
    sep = '' if not sep else sep
    phonemes = _text2phonemes(text, sep=sep, ipa=ipa, tone_letters=tone_letters)
    
    return sep.join(phonemes)


if __name__ == '__main__':
    text_1 = '架車搶軚，要去調返啱個軚尺。' 
    text_2 = '仲所以咩？用粵拼啦！'
    print(text_1, '\n', 
          text2phonemes(text_1, sep=None, ipa=True), '\n',
          text2phonemes(text_1, ipa=True), '\n',
          '\n',
          text2phonemes(text_1, sep=None, ipa=True, tone_letters=True), '\n',
          text2phonemes(text_1, ipa=True, tone_letters=True), '\n',
          '\n',
          text2phonemes(text_1, sep=None, ipa=False), '\n',
          text2phonemes(text_1, ipa=False))
    print(text_2, '\n',
          text2phonemes(text_2, sep=None, ipa=True), '\n',
          text2phonemes(text_2, ipa=True), '\n',
          '\n',
          text2phonemes(text_2, sep=None, ipa=True, tone_letters=True), '\n',
          text2phonemes(text_2, ipa=True, tone_letters=True), '\n',
          '\n',
          text2phonemes(text_2, sep=None, ipa=False), '\n',
          text2phonemes(text_2, ipa=False))

