import re
from typing import List, Set, Tuple

# Comprehensive list of valid pinyin syllables
# This is a subset of the most common syllables - we can expand this
VALID_SYLLABLES: Set[str] = {
    # Single vowels
    'a', 'e', 'i', 'o', 'u', 'ü',
    # Common syllables starting with 'a'
    'a', 'ai', 'an', 'ang', 'ao',
    # Common syllables starting with 'b'
    'ba', 'bai', 'ban', 'bang', 'bao', 'bei', 'ben', 'beng', 'bi', 'bian', 'biao', 'bie', 'bin', 'bing', 'bo', 'bu',
    # Common syllables starting with 'c'
    'ca', 'cai', 'can', 'cang', 'cao', 'ce', 'cen', 'ceng', 'cha', 'chai', 'chan', 'chang', 'chao', 'che', 'chen', 'cheng',
    'chi', 'chong', 'chou', 'chu', 'chua', 'chuai', 'chuan', 'chuang', 'chui', 'chun', 'chuo', 'ci', 'cong', 'cou', 'cu',
    'cuan', 'cui', 'cun', 'cuo',
    # Common syllables starting with 'd'
    'da', 'dai', 'dan', 'dang', 'dao', 'de', 'dei', 'den', 'deng', 'di', 'dian', 'diao', 'die', 'ding', 'diu', 'dong',
    'dou', 'du', 'duan', 'dui', 'dun', 'duo',
    # Common syllables starting with 'e'
    'e', 'ei', 'en', 'eng', 'er',

    # Common syllables starting with 'f'
    'fa', 'fan', 'fang', 'fei', 'fen', 'feng', 'fo', 'fou', 'fu',
    # Common syllables starting with 'g'
    'ga', 'gai', 'gan', 'gang', 'gao', 'ge', 'gei', 'gen', 'geng', 'gong', 'gou', 'gu', 'gua', 'guai', 'guan', 'guang',
    'gui', 'gun', 'guo',
    # Common syllables starting with 'h'
    'ha', 'hai', 'han', 'hang', 'hao', 'he', 'hei', 'hen', 'heng', 'hong', 'hou', 'hu', 'hua', 'huai', 'huan', 'huang',
    'hui', 'hun', 'huo',
    # Common syllables starting with 'j'
    'ji', 'jia', 'jian', 'jiang', 'jiao', 'jie', 'jin', 'jing', 'jiong', 'jiu', 'ju', 'juan', 'jue', 'jun',
    # Common syllables starting with 'k'
    'ka', 'kai', 'kan', 'kang', 'kao', 'ke', 'ken', 'keng', 'kong', 'kou', 'ku', 'kua', 'kuai', 'kuan', 'kuang', 'kui',
    'kun', 'kuo',
    # Common syllables starting with 'l'
    'la', 'lai', 'lan', 'lang', 'lao', 'le', 'lei', 'leng', 'li', 'lia', 'lian', 'liang', 'liao', 'lie', 'lin', 'ling',
    'liu', 'long', 'lou', 'lu', 'lü', 'luan', 'lüe', 'lun', 'luo',
    # Common syllables starting with 'm'
    'ma', 'mai', 'man', 'mang', 'mao', 'me', 'mei', 'men', 'meng', 'mi', 'mian', 'miao', 'mie', 'min', 'ming', 'miu',
    'mo', 'mou', 'mu',
    # Common syllables starting with 'n'
    'na', 'nai', 'nan', 'nang', 'nao', 'ne', 'nei', 'nen', 'neng', 'ni', 'nian', 'niang', 'niao', 'nie', 'nin', 'ning',
    'niu', 'nong', 'nou', 'nu', 'nü', 'nuan', 'nüe', 'nuo',
    # Common syllables starting with 'o'
    'o', 'ou',

    # Common syllables starting with 'p'
    'pa', 'pai', 'pan', 'pang', 'pao', 'pei', 'pen', 'peng', 'pi', 'pian', 'piao', 'pie', 'pin', 'ping', 'po', 'pou', 'pu',
    # Common syllables starting with 'q'
    'qi', 'qia', 'qian', 'qiang', 'qiao', 'qie', 'qin', 'qing', 'qiong', 'qiu', 'qu', 'quan', 'que', 'qun',
    # Common syllables starting with 'r'
    'ran', 'rang', 'rao', 're', 'ren', 'reng', 'ri', 'rong', 'rou', 'ru', 'ruan', 'rui', 'run', 'ruo', 'r',
    # Common syllables starting with 's'
    'sa', 'sai', 'san', 'sang', 'sao', 'se', 'sen', 'seng', 'sha', 'shai', 'shan', 'shang', 'shao', 'she', 'shei', 'shen', 'sheng',
    'shi', 'shou', 'shu', 'shua', 'shuai', 'shuan', 'shuang', 'shui', 'shun', 'shuo', 'si', 'song', 'sou', 'su', 'suan',
    'sui', 'sun', 'suo',
    # Common syllables starting with 't'
    'ta', 'tai', 'tan', 'tang', 'tao', 'te', 'teng', 'ti', 'tian', 'tiao', 'tie', 'ting', 'tong', 'tou', 'tu', 'tuan',
    'tui', 'tun', 'tuo',
    # Common syllables starting with 'w'
    'wa', 'wai', 'wan', 'wang', 'wei', 'wen', 'weng', 'wo', 'wu',
    # Common syllables starting with 'x'
    'xi', 'xia', 'xian', 'xiang', 'xiao', 'xie', 'xin', 'xing', 'xiong', 'xiu', 'xu', 'xuan', 'xue', 'xun',
    # Common syllables starting with 'y'
    'ya', 'yan', 'yang', 'yao', 'yo', 'ye', 'yi', 'yin', 'ying', 'yong', 'you', 'yu', 'yuan', 'yue', 'yun',
    # Common syllables starting with 'z'
    'za', 'zai', 'zan', 'zang', 'zao', 'ze', 'zei', 'zen', 'zeng', 'zha', 'zhai', 'zhan', 'zhang', 'zhao', 'zhe', 'zhen',
    'zheng', 'zhi', 'zhong', 'zhou', 'zhu', 'zhua', 'zhuai', 'zhuan', 'zhuang', 'zhui', 'zhun', 'zhuo', 'zi', 'zong',
    'zou', 'zu', 'zuan', 'zui', 'zun', 'zuo',
}

def remove_tone_marks(pinyin: str) -> str:
    """Remove tone marks from pinyin and convert to lowercase."""
    # Define tone mark mappings
    tone_marks = {
        'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
        'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
        'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
        'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
        'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
        'ǖ': 'ü', 'ǘ': 'ü', 'ǚ': 'ü', 'ǜ': 'ü'
    }
    
    result = ''
    for char in pinyin.lower():
        result += tone_marks.get(char, char)
    return result

def find_valid_splits(pinyin: str, num_syllables: int) -> List[List[str]]:
    """
    Find all possible valid splits of a pinyin string into exactly num_syllables parts.
    Returns a list of lists, where each inner list contains the valid syllables.
    """
    pinyin = remove_tone_marks(pinyin)
    valid_splits = []
    
    def try_split(remaining: str, current_split: List[str], remaining_syllables: int):
        if remaining_syllables == 0:
            if not remaining:  # If we've used all characters
                valid_splits.append(current_split.copy())
            return
        
        # Try all possible lengths for the next syllable
        for i in range(1, len(remaining) + 1):
            next_syllable = remaining[:i]
            if next_syllable in VALID_SYLLABLES:
                current_split.append(next_syllable)
                try_split(remaining[i:], current_split, remaining_syllables - 1)
                current_split.pop()
    
    try_split(pinyin, [], num_syllables)
    return valid_splits

def split_pinyin(line_index: int, pinyin: str, hanzi: str) -> str:
    """
    Split a pinyin string into syllables based on the hanzi.
    For single hanzi, no splitting is needed.
    For multiple hanzi, find all valid splits that match the hanzi length.
    Returns the pinyin with spaces between syllables.
    """
    status = "success"
    pinyin = pinyin.replace("'", " ")
    # If it's already split, return as is
    if len(hanzi) == len(pinyin.split(' ')):
        status = "no_split"
        return pinyin, status
    
    # If it's a single syllable, return as is
    if remove_tone_marks(pinyin) in VALID_SYLLABLES and len(hanzi) == 1:
        status = "no_split"
        return pinyin, status
    
    # replace ' ' or \' with ''
    pinyin = pinyin.replace(' ', '').replace("'", "")
    # Find all valid splits that match the hanzi length
    valid_splits = find_valid_splits(pinyin, len(hanzi))
    
    if not valid_splits:
        # If no valid splits found, return as is
        print(f"No valid splits found for '{hanzi}' ({pinyin}) at line {line_index}")
        status = "no_valid"
        return pinyin, status
    
    if len(valid_splits) > 1:
        status = "multiple_valid"
        # If multiple valid splits exist, print them for user decision
        print(f"\nMultiple valid splits found for '{hanzi}' ({pinyin}) at line {line_index}:")
        for i, split in enumerate(valid_splits, 1):
            # Convert each syllable back to its original form with tone marks
            original_split = []
            remaining = pinyin
            for syllable in split:
                original_split.append(remaining[:len(syllable)])
                remaining = remaining[len(syllable):]
            print(f"{i}. {' '.join(original_split)}")
        
        # Use the first split
        first_split = valid_splits[0]
        # Convert back to original form with tone marks
        result = []
        remaining = pinyin
        for syllable in first_split:
            result.append(remaining[:len(syllable)])
            remaining = remaining[len(syllable):]
        return ' '.join(result), status
    
    # If only one valid split exists, use it
    first_split = valid_splits[0]
    # Convert back to original form with tone marks
    result = []
    remaining = pinyin
    for syllable in first_split:
        result.append(remaining[:len(syllable)])
        remaining = remaining[len(syllable):]
    return ' '.join(result), status