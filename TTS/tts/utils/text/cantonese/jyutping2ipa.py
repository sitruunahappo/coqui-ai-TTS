'''Dictionaries for Jyutping to IPA

As always, go check https://jyutping.org/en/jyutping/

People usually just make all possible pronunciation combinations, which 
is ideal for Cantonese also, as compared with English, it is still
somehow 'not too much'. Also, Cantonese has more rules than Putonghua

However, when I started to list all possibilities, I felt real pain, so 
I decided to list phonemes instead, even though I would have to handle 
the rules.

Also because of this, those coda were moved out of the main dict, or 
I would have to handle a list with three items
'''

# Called INIT, but it includes initials and nucleus
INIT_DICT = {
    'p': ['pʰ'],
    't': ['tʰ'],
    'k': ['kʰ'],
    
    'b': ['p'],
    'd': ['t'],
    'g': ['k'],
    'kw': ['kʷ'],
    'gw': ['kʷʰ'],
    
    'z': ['tsʰ'],
    'c': ['ts'],

    'm': ['m'],
    'n': ['n'],
    'ng': ['ŋ'],

    'f': ['f'],
    's': ['s'],
    'h': ['h'],
    'w': ['w'],
    'j': ['j'],
    'l': ['l'],

    'i': ['iː', 'e'],
    'yu': ['y'],
    'u': ['uː', 'o'],
    'e': ['ɛː', 'e'],
    'oe': ['œː'],
    'o': ['ɔː', 'o'],
    'a': ['ɐ'],
    'aa': ['aː'],
    }


CODA_DICT = {
    'p': 'p̚',
    't': 't̚',
    'k': 'k̚',
    
    'm': 'm',
    'n': 'n',
    'ng': 'ŋ',

    'i': 'i',
    'u': 'u',
    }


# Tones in digit system 
TONE_DICT = {
    '1': '55', 
    '2': '25',
    '3': '33',
    '4': '21',
    '5': '23',
    '6': '22',
    }

# Separate entering tones for convenience 
ENTERING_TONES = {
    '1': '5',
    '3': '3',
    '6': '2',
    }


# Letters for the checking tones are the same with non-entering tones 
# in most of what I read. I would like to argue it a little bit but I 
# guess no one gonna use these letters in real life
TONE_LETTERS = {
    '1': '˥', 
    '2': '˧˥',
    '3': '˧',
    '4': '˨˩',
    '5': '˩˧',
    '6': '˨',
    }
