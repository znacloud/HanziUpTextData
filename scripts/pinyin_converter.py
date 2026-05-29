
import re

def pinyin_to_number(pinyin):
    # 声调符号与数字的映射
    tone_map = {
        'ā': ('a', 1), 'á': ('a', 2), 'ǎ': ('a', 3), 'à': ('a', 4),
        'ō': ('o', 1), 'ó': ('o', 2), 'ǒ': ('o', 3), 'ò': ('o', 4),
        'ē': ('e', 1), 'é': ('e', 2), 'ě': ('e', 3), 'è': ('e', 4),
        'ī': ('i', 1), 'í': ('i', 2), 'ǐ': ('i', 3), 'ì': ('i', 4),
        'ū': ('u', 1), 'ú': ('u', 2), 'ǔ': ('u', 3), 'ù': ('u', 4),
        'ǖ': ('v', 1), 'ǘ': ('v', 2), 'ǚ': ('v', 3), 'ǜ': ('v', 4)
    }
    
    # 特殊处理ü的情况（j/q/x后面的u实际是ü）
    #if re.search(r'[jqx][uü]', pinyin):
    #    pinyin = pinyin.replace('u', 'ü').replace('v', 'ü')
    
    result = []
    tone_num = 0
    
    for char in pinyin:
        if char in tone_map:
            plain_char, tone_num = tone_map[char]
            result.append(plain_char)
        else:
            # 处理普通字母或ü的两种写法
            #if char == 'ü':
            #    result.append('v')
            #else:
            result.append(char)
    
    # 组合结果并添加声调数字（无声调默认为5）
    return ''.join(result) + ' ' + str(tone_num if tone_num != 0 else 5)

# 测试示例
if __name__ == '__main__':
    test_cases = ['zhōng', 'guó', 'rén', 'mín', 'jū', 'nǚ', 'xuě', 'lüè', 'quán']
    for pinyin in test_cases:
        print(f"{pinyin} -> {pinyin_to_number(pinyin)}")
