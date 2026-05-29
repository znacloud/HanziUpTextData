from bs4 import BeautifulSoup
import re

html1 = """<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>的</x-hw><x-pr> de</x-pr>
<dt><x-sn>①</x-sn><x-gram>助</x-gram>用在作定语的词或短语后面<x-f>。</x-f></dt>
<dt><x-a>a.</x-a> 表示对中心语的领属关系，对事物的性质、属性、范围等加以限定<x-f>。</x-f></dt><x-dd>▷</x-dd><x-ex>我<x-key>的</x-key>书</x-ex><x-ex><x-lb> | </x-lb>镀金<x-key>的</x-key>首饰</x-ex><x-ex><x-lb> | </x-lb>幸福<x-key>的</x-key>童年</x-ex>
<dt><x-a>b.</x-a> 表示对中心语加以描写<x-f>。</x-f></dt><dd><x-ex>蓝蓝<x-key>的</x-key>天</x-ex><x-ex><x-lb> | </x-lb>愁眉苦脸<x-key>的</x-key>样子</x-ex></dd>
<dt><x-sn>②</x-sn><sbl>→</sbl><x-g>助</x-g>用在名词、动词或形容词后面，构成名词性的“的”字结构<x-f>。</x-f></dt><dd><x-ex>北京<x-key>的</x-key>、上海<x-key>的</x-key>都来了</x-ex><x-ex><x-lb> | </x-lb>有大<x-key>的</x-key>、小<x-key>的</x-key>、中不溜<x-er>儿</x-er><x-key>的</x-key></x-ex><x-ex><x-lb> | </x-lb>说<x-key>的</x-key>比唱<x-key>的</x-key>还好听<x-f>。</x-f></x-ex></dd>
<dt><x-sn>③</x-sn><sbl>→</sbl><x-g>助</x-g>用在句末，表示肯定的语气或已然的语气<x-f>。</x-f></dt><dd><x-ex>你这样做是行不通<x-key>的</x-key></x-ex><x-ex><x-lb> | </x-lb>老王什么时候走<x-key>的</x-key>?</x-ex></dd>
<dt><x-sn>④</x-sn><sbl>→</sbl><x-g>助</x-g>用在某些句子的动词和宾语之间，强调动作的施事者、受事者或时间、地点、方式等<x-f>。</x-f></dt><dd><x-ex>主任签<x-key>的</x-key>字</x-ex><x-ex><x-lb> | </x-lb>回来坐<x-key>的</x-key>飞机</x-ex><x-ex><x-lb> | </x-lb>他昨天夜里犯<x-key>的</x-key>病</x-ex><x-ex><x-lb> | </x-lb>我在上海念<x-key>的</x-key>中学<x-f>。</x-f></x-ex></dd><t-note><x-lb>用法说明</x-lb>助词“的”在某些歌词、唱词或个别惯用语中，有时读 dì<x-f>。</x-f></t-note><x-ref>另见</x-ref><a href="entry://的" type="seealso">dī</a><x-f>；</x-f><a href="entry://的" type="seealso">dí</a><x-f>；</x-f><a href="entry://的" type="seealso">dì</a><x-f>。</x-f></dt><hr><dt class='title'><x-hw>的</x-hw><x-pr> dī</x-pr>
<dt><x-gram>名</x-gram>的士<x-f>。</x-f></dt><dd><x-ex>打<x-key>的</x-key></x-ex></dd>
<dt><x-ref>另见</x-ref><a href="entry://的" type="seealso">de</a><x-f>；</x-f><a href="entry://的" type="seealso">dí</a><x-f>；</x-f><a href="entry://的" type="seealso">dì</a><x-f>。</x-f></dt><hr><dt class='title'><x-hw>的</x-hw><x-pr> dì</x-pr>
<dt><x-gram>名</x-gram>箭靶的中心<x-f>。</x-f></dt><dd><x-ex>众矢之<x-key>的</x-key></x-ex><x-ex><x-lb> | </x-lb>有<x-key>的</x-key>放矢</x-ex><x-lb> | </x-lb>◇一语破<x-key>的</x-key><x-ex><x-lb> | </x-lb>目<x-key>的</x-key></x-ex></dd>
<dt><x-ref>另见</x-ref><a href="entry://的" type="seealso">de</a><x-f>；</x-f><a href="entry://的" type="seealso">dī</a><x-f>；</x-f><a href="entry://的" type="seealso">dí</a><x-f>。</x-f></dt><hr><dt class='title'><x-hw>的</x-hw><x-pr> dí</x-pr>
<dt><x-gram>形</x-gram>确实；实在<x-f>。</x-f></dt><dd><x-ex><x-key>的</x-key>证（确凿的证据）</x-ex><x-ex><x-lb> | </x-lb><x-key>的</x-key>确</x-ex></dd>
<dt><x-ref>另见</x-ref><a href="entry://的" type="seealso">de</a><x-f>；</x-f><a href="entry://的" type="seealso">dī</a><x-f>；</x-f><a href="entry://的" type="seealso">dì</a><x-f>。</x-f>
"""

html2 = """
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>我</x-hw><x-pr> wǒ</x-pr>
<dt><x-sn>①</x-sn><x-gram>代</x-gram>说话人称自己<x-f>。</x-f></dt><dd><x-ex><x-key>我</x-key>认识你</x-ex><x-ex><x-lb> | </x-lb>他是<x-key>我</x-key>的老师</x-ex></dd>
<dt><x-sn>②</x-sn><sbl>→</sbl><x-g>代</x-g>称自己的一方，相当于“我们”<x-f>。</x-f></dt><dd><x-ex><x-key>我</x-key>国</x-ex><x-ex><x-lb> | </x-lb><x-key>我</x-key>军</x-ex><x-ex><x-lb> | </x-lb><x-key>我</x-key>校</x-ex><x-ex><x-lb> | </x-lb><x-key>我</x-key>厂</x-ex><x-ex><x-lb> | </x-lb>敌<x-key>我</x-key>双方</x-ex></dd>
<dt><x-sn>③</x-sn><sbl>→</sbl><x-g>代</x-g>用于“你” “我”对举，泛指许多人<x-f>。</x-f></dt><dd><x-ex>你来<x-key>我</x-key>往</x-ex><x-ex><x-lb> | </x-lb>你一言，<x-key>我</x-key>一语</x-ex></dd>
<dt><x-sn>④</x-sn><sbl>→</sbl><x-g>代</x-g>自己<x-f>。</x-f></dt><dd><x-ex>自<x-key>我</x-key>介绍</x-ex><x-ex><x-lb> | </x-lb>忘<x-key>我</x-key>工作</x-ex></dd>
"""

html3 = """
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>上台阶</x-hw><x-pr> shàngtáijiē</x-pr>
<dt>登上台阶或沿着台阶往上走；比喻达到一个新的高度或上升到一个新的水平<x-f>。</x-f></dt><dd><x-ex>经济建设连年<x-key>上台阶</x-key><x-f>。</x-f></x-ex></dd>
"""

html4="""
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>上学</x-hw><x-pr> shàngxué</x-pr>
<dt><x-sn>①</x-sn><x-gram>动</x-gram>到学校学习<x-f>。</x-f></dt>
<dt><x-sn>②</x-sn><x-g>动</x-g> 儿童开始入学<x-f>。</x-f></dt><dd><x-ex>这孩子明年该<x-key>上学</x-key>了<x-f>。</x-f></x-ex></dd>
"""

html5="""
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>上梁不正下梁歪</x-hw><x-pr> shàngliáng bù zhèng xiàliáng wāi</x-pr>
<dt>比喻领导或长辈不正派，下边的人就会跟着学坏<x-f>。</x-f></dt>
"""

html6="""
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>读</x-hw><x-pr> dòu</x-pr>（讀）
<dt><x-gram>名</x-gram>旧指诵读古文时文句中需要稍作停顿的地方（比“句”停顿要短）<x-f>。</x-f></dt><dd><x-ex>句<x-key>读</x-key></x-ex></dd>
<dt><x-ref>另见</x-ref><a href="entry://读" type="seealso">dú</a><x-f>。</x-f></dt><hr><dt class='title'><x-hw>读</x-hw><x-pr> dú</x-pr>（讀）
<dt><x-sn>①</x-sn><x-gram>动</x-gram>看着文字并念出声来<x-f>。</x-f></dt><dd><x-ex><x-key>读</x-key>一遍课文</x-ex><x-ex><x-lb> | </x-lb>朗<x-key>读</x-key></x-ex><x-ex><x-lb> | </x-lb>宣<x-key>读</x-key></x-ex></dd>
<dt><x-sn>②</x-sn><sbl>→</sbl><x-g>动</x-g>看着文字并理解其意义<x-f>。</x-f></dt><dd><x-ex>这本书值得一<x-key>读</x-key></x-ex><x-ex><x-lb> | </x-lb>阅<x-key>读</x-key></x-ex></dd>
<dt><x-sn>③</x-sn><x-g>动</x-g> 指上学或学习<x-f>。</x-f></dt><dd><x-ex>他只<x-key>读</x-key>过初中</x-ex><x-ex><x-lb> | </x-lb>你<x-key>读</x-key>什么专业?</x-ex><x-ex><x-lb> | </x-lb>走<x-key>读</x-key></x-ex></dd>
<dt><x-sn>④</x-sn><sbl>→</sbl><x-g>动</x-g>读作；读音是<x-f>。</x-f></dt><dd><x-ex>这个字<x-key>读</x-key>去声，不<x-key>读</x-key>阴平<x-f>。</x-f></x-ex></dd><t-note><x-lb>用法说明</x-lb>“读”字一般读 dú；读 dòu，专指诵读时句中的停顿。旧时把读书时短暂的停顿叫 dòu，写作“读”，较长的停顿叫“句”，合称“句读”<x-f>。</x-f></t-note><x-ref>另见</x-ref><a href="entry://读" type="seealso">dòu</a><x-f>。</x-f>
"""
html7="""
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>沙袋</x-hw><x-pr> shādài</x-pr>
<dt><x-gram>名</x-gram>装有沙子的口袋。用于军事防御、防洪、防火、体育锻炼等<x-f>。</x-f></dt>
"""

html8="""
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script>一 1 <x-pr> yī</x-pr>
<dt><x-sn>①</x-sn><x-gram>数</x-gram>数字，最小的正整数<x-f>。</x-f></dt>
<dt><x-sn>②</x-sn><sbl>→</sbl><x-g>数</x-g>指同一或一样<x-f>。</x-f></dt><dd><x-ex>咱们坐<x-key>一</x-key>趟车</x-ex><x-ex><x-lb> | </x-lb>他俩在<x-key>一</x-key>个单位</x-ex><x-ex><x-lb> | </x-lb>长短不<x-key>一</x-key></x-ex></dd>
<dt><x-sn>③</x-sn><sbl>→</sbl><x-g>数</x-g>指满、全或整个<x-f>。</x-f></dt><dd><x-ex>坐了满满<x-key>一</x-key>车人</x-ex><x-ex><x-lb> | </x-lb><x-key>一</x-key>身土</x-ex><x-ex><x-lb> | </x-lb>书堆了<x-key>一</x-key>桌子</x-ex><x-ex><x-lb> | </x-lb>病了<x-key>一</x-key>夏天</x-ex><x-ex><x-lb> | </x-lb><x-key>一</x-key>如所见</x-ex></dd>
<dt><x-sn>④</x-sn>数指专一或单一<x-f>。</x-f></dt><dd><x-ex><x-key>一</x-key>心<x-key>一</x-key>意</x-ex><x-ex><x-lb> | </x-lb><x-key>一</x-key>色的两层小楼</x-ex></dd>
<dt><x-sn>⑤</x-sn><sbl>→</sbl><x-g>数</x-g>指某一<x-f>。</x-f></dt><dd><x-ex><x-key>一</x-key>天晚上</x-ex><x-ex><x-lb> | </x-lb>有<x-key>一</x-key>年</x-ex></dd>
<dt><x-sn>⑥</x-sn><sbl>→</sbl><x-g>数</x-g>指每一<x-f>。</x-f></dt><dd><x-ex><x-key>一</x-key>组八个人</x-ex><x-ex><x-lb> | </x-lb><x-key>一</x-key>年一次</x-ex><x-ex><x-lb> | </x-lb><x-key>一</x-key>人两块钱</x-ex></dd>
<dt><x-sn>⑦</x-sn><sbl>→</sbl><x-g>数</x-g>指另一或又一<x-f>。</x-f></dt><dd><x-ex>乌贼<x-key>一</x-key>名墨斗鱼</x-ex><x-ex><x-lb> | </x-lb>这种习俗起源于唐代，<x-key>一</x-key>说起源于宋代<x-f>。</x-f></x-ex></dd>
<dt><x-sn>⑧</x-sn><sbl>→</sbl><x-g>副</x-g>表示猛然发出某种动作或突然出现某种情况<x-f>。</x-f></dt><dd><x-ex>往起<x-key>一</x-key>站</x-ex><x-ex><x-lb> | </x-lb>右手<x-key>一</x-key>挥</x-ex><x-ex><x-lb> | </x-lb>眼前<x-key>一</x-key>黑</x-ex></dd>
<dt><x-sn>⑨</x-sn> <x-g>副</x-g> 与“就” “便”等副词相呼应，表示前一动作或情况一旦发生，紧跟着就要出现另一动作或情况<x-f>。</x-f></dt><dd><x-ex><x-key>一</x-key>叫就来</x-ex><x-ex><x-lb> | </x-lb><x-key>一</x-key>看就会</x-ex><x-ex><x-lb> | </x-lb><x-key>一</x-key>问便知</x-ex></dd>
<dt><x-sn>⑩</x-sn><sbl>→</sbl><x-g>副</x-g>用在重叠的动词之间，表示动作是短暂的或尝试性的<x-f>。</x-f></dt><dd><x-ex>跳<x-key>一</x-key>跳</x-ex><x-ex><x-lb> | </x-lb>笑<x-key>一</x-key>笑</x-ex><x-ex><x-lb> | </x-lb>瞧<x-key>一</x-key>瞧</x-ex><x-ex><x-lb> | </x-lb>说<x-key>一</x-key>说</x-ex></dd><t-note><x-lb>用法说明</x-lb>㊀“一”在句中要发生变调现象：1.用作序数或用在句尾时仍读阴平，如“一、思想好，二、学习好” “第一” “十月一日” “一排二班” “感情专一”;2.用在去声前变为阳平，如“一并” “一定” “一望无际”;3.用在阴平、阳平、上声前，变为去声，如“一般” “一回” “一览无余”。㊁数字“一”的大写是“壹”<x-f>。</x-f></t-note></dt><hr><dt class='title'>一 2 <x-pr> yī</x-pr><br><x-gram>名</x-gram>我国民族音乐中传统的记音符号，表示音阶上的一级，相当于简谱的“7̣̣”<x-f>。</x-f></dt>
"""

html9 = """
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>缂</x-hw><x-pr> kè</x-pr>（緙）缂丝<x-pr> kèsī</x-pr> <x-g>动</x-g> 
<dt>指将绘画织在丝织品上。织成以后，看上去图形好像刻镂而成。这种工艺始于宋代，主要流行于苏州<x-f>。</x-f></dt> <x-g>名</x-g> 
<dt>用这种工艺织成的衣料和物品<x-f>。</x-f></dt>
"""

html10 = """
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>似</x-hw><x-pr> shì</x-pr>似的<x-pr> shìde</x-pr>助
<dt>用在词或短语之后，表示跟某种事物或情况相像<x-f>。</x-f></dt><dd><x-ex>淋得落汤鸡<x-key>似的</x-key></x-ex><x-ex><x-lb> | </x-lb>他像兔子<x-key>似的</x-key>跑了</x-ex><x-ex><x-lb> | </x-lb>看起来很轻松<x-key>似的</x-key><x-f>。</x-f></x-ex></dd><t-note><x-lb>用法说明</x-lb>㊀“似”这里不读 sì。㊁“似的”不宜写作“是的”<x-f>。</x-f></t-note><x-ref>另见</x-ref><a href="entry://似" type="seealso">sì</a><x-f>。</x-f></dt><hr><dt class='title'><x-hw>似</x-hw><x-pr> sì</x-pr>（*佀）
<dt><x-sn>①</x-sn><x-gram>动</x-gram>像；相类<x-f>。</x-f></dt><dd><x-ex>类<x-key>似</x-key></x-ex><x-ex><x-lb> | </x-lb>骄阳<x-key>似</x-key>火</x-ex></dd>
<dt><x-sn>②</x-sn><sbl>→</sbl><x-g>副</x-g>表示不确定，相当于“仿佛” “好像”<x-f>。</x-f></dt><dd><x-ex><x-key>似</x-key>曾相识</x-ex><x-ex><x-lb> | </x-lb><x-key>似</x-key>是而非</x-ex></dd>
<dt><x-sn>③</x-sn><sbl>→</sbl><x-g>介</x-g>用在“好” “强”之类的形容词后面，引进比较的对象<x-f>。</x-f></dt><dd><x-ex>日子一天好<x-key>似</x-key>一天</x-ex><x-ex><x-lb> | </x-lb>身体一年强<x-key>似</x-key>一年<x-f>。</x-f></x-ex></dd><t-note><x-lb>用法说明</x-lb>“似的”的“似”读 shì，不读 sì<x-f>。</x-f></t-note><x-ref>另见</x-ref><a href="entry://似" type="seealso">shì</a><x-f>。</x-f>
"""

html11 = """
<link rel="stylesheet" type="text/css" href="HYGF2.css"><script src='HYGF2.js'></script><x-hw>给付</x-hw><x-pr> jǐfù</x-pr><br><x-gram>动</x-gram>交付<x-f>。</x-f></dt><dd><x-ex><x-key>给付</x-key>赔款</x-ex><x-ex><x-lb> | </x-lb><x-key>给付</x-key>保险金</x-ex></dd>
"""

html = html10





def is_special_pattern(pinyin_tag):
    """Check if this pinyin tag is part of the special pattern where grammatical info appears between definitions (like html9)"""
    # Check if there's another x-pr tag after this one
    next_x_pr = pinyin_tag.find_next("x-pr")
    if next_x_pr:
        # Check if there are x-g tags before or between dt tags
        current_dt = pinyin_tag.find_next("dt")
        if current_dt:
            # Look for x-g tags between the pinyin tag and the first dt tag
            current = pinyin_tag.find_next_sibling()
            while current and current != current_dt:
                if current.name == "x-g":
                    return True
                current = current.find_next_sibling()
            
            # Also check between dt tags
            next_dt = current_dt.find_next("dt")
            if next_dt:
                current = current_dt.find_next_sibling()
                while current and current != next_dt:
                    if current.name == "x-g":
                        return True
                    current = current.find_next_sibling()
    return False


def extract_special_pattern_entries(soup, pinyin_tag, hanzi):
    """Handle special pattern where grammatical info appears between definitions (like html9)"""
    # Find all pinyin readings for this hanzi
    pinyin_readings = []
    words = []  # Track the words associated with each pinyin
    current_pinyin_tag = pinyin_tag
    
    # Collect all pinyin tags that belong to this hanzi entry
    while current_pinyin_tag:
        pinyin_readings.append(current_pinyin_tag.get_text(strip=True))
        
        # Extract the word from text content between this pinyin tag and the next one
        word = ""
        current = current_pinyin_tag.find_next_sibling()
        
        # Look for text content between this pinyin tag and the next one
        while current and current.name != "x-pr":
            if isinstance(current, str):
                # Extract Chinese characters from text content
                text_content = current.strip()
                if text_content:
                    # Remove parentheses and other non-Chinese characters, but keep the word
                    # For example: "（緙）缂丝" should extract "缂丝"
                    word_matches = re.findall(r'[一-龯]+', text_content)
                    if word_matches:
                        # Take the longest Chinese character sequence (likely the word)
                        longest_word = max(word_matches, key=len)
                        if len(longest_word) > len(word):
                            word = longest_word
            current = current.find_next_sibling()
        
        # If no word found in text content, use the hanzi for single character entries
        if not word:
            if len(pinyin_readings) == 1:
                word = hanzi
            else:
                # For subsequent pinyin readings, look for the word in the text before this pinyin tag
                # This handles cases where the word appears before the pinyin tag
                prev_sibling = current_pinyin_tag.previous_sibling
                if prev_sibling and isinstance(prev_sibling, str):
                    text_content = prev_sibling.strip()
                    if text_content:
                        word_matches = re.findall(r'[一-龯]+', text_content)
                        if word_matches:
                            word = max(word_matches, key=len)
        
        words.append(word)
        
        # Look for the next pinyin tag
        next_pinyin_tag = current_pinyin_tag.find_next("x-pr")
        if next_pinyin_tag:
            # Check if this next pinyin tag is still part of the same entry
            # (not separated by hr or title dt)
            between_tags = []
            current = current_pinyin_tag.find_next_sibling()
            while current and current != next_pinyin_tag:
                if current.name == "hr" or (current.name == "dt" and "title" in current.get("class", [])):
                    # Found a separator, so next pinyin is for a different entry
                    next_pinyin_tag = None
                    break
                current = current.find_next_sibling()
            current_pinyin_tag = next_pinyin_tag
        else:
            break
    
    # Create entry with hanzi and words
    entry = {
        "hanzi": hanzi,
        "pinyin": pinyin_readings,  # Now a list of pinyin readings
        "words": words,  # List of words associated with each pinyin
        "senses": []
    }
    
    # Find all dt tags that follow this pinyin tag
    current = pinyin_tag
    current_pos = None
    
    while True:
        current = current.find_next_sibling()
        if current is None or current.name == "hr":
            break
            
        # Check for grammatical information between dt tags
        if current.name == "x-g":
            current_pos = current.get_text(strip=True)
            continue
            
        if current.name == "dt":
            # Extract definition
            for tag in current.find_all(["x-sn", "x-gram", "x-g", "x-f", "sbl"]):
                tag.extract()
            definition = current.get_text(" ", strip=True)
            
            if definition.strip().startswith("用法说明"):
                continue
                
            # Look for examples in following dd tags
            examples = []
            dd_sib = current.find_next_sibling()
            if dd_sib and dd_sib.name == "dd":
                for ex in dd_sib.find_all("x-ex"):
                    examples.append(ex.get_text(" ", strip=True))
            
            entry["senses"].append({
                "pos": current_pos,
                "definition": definition,
                "examples": examples
            })
            
            # Reset pos for next definition
            current_pos = None
    
    return entry


def extract_hanzi_cihui_entries(input_html):
    soup = BeautifulSoup(input_html, "html.parser")
    entries = []
    processed_pinyin_tags = set()  # Track processed pinyin tags
    
    # Find all x-pr tags (pinyin tags)
    pinyin_tags = soup.find_all("x-pr")
    
    for pinyin_tag in pinyin_tags:
        # Skip if already processed as part of a special pattern
        if id(pinyin_tag) in processed_pinyin_tags:
            continue
            
        # Try to find hanzi from x-hw tag first
        hw_tag = pinyin_tag.find_previous("x-hw")
        if hw_tag:
            hanzi = hw_tag.get_text(strip=True)
        else:
            # If no x-hw tag, look for hanzi in the text before x-pr
            # Get the previous sibling text content
            prev_sibling = pinyin_tag.previous_sibling
            if prev_sibling and isinstance(prev_sibling, str):
                # Extract hanzi from text like "一 1 " or "一 "
                text_before = prev_sibling.strip()
                # Use regex to extract Chinese characters (could be multiple)
                hanzi_matches = re.findall(r'[一-龯]+', text_before)
                if hanzi_matches:
                    # Take the first Chinese character sequence found
                    hanzi = hanzi_matches[0]
                else:
                    continue  # Skip if no hanzi found
            else:
                continue  # Skip if no text before x-pr
        
        # Check if this is the special pattern
        if is_special_pattern(pinyin_tag):
            # Handle special pattern using separate function
            entry = extract_special_pattern_entries(soup, pinyin_tag, hanzi)
            entries.append(entry)
            
            # Mark all pinyin tags in this entry as processed
            current_pinyin_tag = pinyin_tag
            while current_pinyin_tag:
                processed_pinyin_tags.add(id(current_pinyin_tag))
                next_pinyin_tag = current_pinyin_tag.find_next("x-pr")
                if next_pinyin_tag:
                    # Check if this next pinyin tag is still part of the same entry
                    current = current_pinyin_tag.find_next_sibling()
                    while current and current != next_pinyin_tag:
                        if current.name == "hr" or (current.name == "dt" and "title" in current.get("class", [])):
                            next_pinyin_tag = None
                            break
                        current = current.find_next_sibling()
                    current_pinyin_tag = next_pinyin_tag
                else:
                    break
            continue
        
        # Original logic for standard pattern
        pinyin = pinyin_tag.get_text(strip=True)
        entry = {
            "hanzi": hanzi,
            "pinyin": pinyin,
            "senses": []
        }
        current = pinyin_tag
        processed_subdefs = set()
        while True:
            current = current.find_next_sibling()
            if current is None or (current.name == "hr") or (current.name == "dt" and "title" in current.get("class", [])):
                break
            if current.name == "dt":
                # Skip sub-definitions that have already been processed
                if id(current) in processed_subdefs:
                    continue
                # Skip sub-definitions in the main loop
                if current.find("x-a"):
                    continue
                # Only skip <dt> if it is a cross-reference
                if current.find("x-ref"):
                    continue
                gram = current.find("x-gram") or current.find("x-g")
                pos = gram.get_text(strip=True) if gram else None
                for tag in current.find_all(["x-sn", "x-gram", "x-g", "x-f", "sbl"]):
                    tag.extract()
                definition = current.get_text(" ", strip=True)
                if definition.strip().startswith("用法说明"):
                    # print(f"Skipping {definition}")
                    continue
                # Scan forward for sub-definitions, skipping <dd>
                sib = current.find_next_sibling()
                found_subdef = False
                while sib:
                    # Skip <dd>
                    if sib.name == "dd":
                        sib = sib.find_next_sibling()
                        continue
                    if sib.name == "dt" and sib.find("x-a"):
                        found_subdef = True
                        processed_subdefs.add(id(sib))
                        # Sub-definition: create a new sense with main def + sub-def
                        for tag in sib.find_all(["x-a", "x-f"]):
                            tag.extract()
                        sub_def = sib.get_text(" ", strip=True)
                        if sub_def.strip().startswith("用法说明"):
                            print(f"Skipping sub-definition: {sub_def}")
                            sub_def = ""
                        full_def = definition + " " + sub_def if sub_def else definition
                        # Collect all <x-ex> siblings and all <x-ex> in following <dd> (if any), until next <dt> or <hr>
                        examples = []
                        ex_sib = sib.find_next_sibling()
                        while ex_sib and ex_sib.name != "dt" and ex_sib.name != "hr":
                            if ex_sib.name == "x-ex":
                                examples.append(ex_sib.get_text(" ", strip=True))
                            elif ex_sib.name == "dd":
                                for ex in ex_sib.find_all("x-ex"):
                                    examples.append(ex.get_text(" ", strip=True))
                            ex_sib = ex_sib.find_next_sibling()
                        entry["senses"].append({
                            "pos": pos,
                            "definition": full_def,
                            "examples": examples
                        })
                        sib = sib.find_next_sibling()
                        continue
                    # Stop at next main <dt> or <hr>
                    if sib.name == "dt" or sib.name == "hr":
                        break
                    sib = sib.find_next_sibling()
                if found_subdef:
                    continue  # If there were sub-definitions, do not output the main definition
                # If no sub-definitions, add the main definition as a sense
                examples = []
                dd_sib = current.find_next_sibling()
                if dd_sib and dd_sib.name == "dd":
                    for ex in dd_sib.find_all("x-ex"):
                        examples.append(ex.get_text(" ", strip=True))
                entry["senses"].append({
                    "pos": pos,
                    "definition": definition,
                    "examples": examples
                })
        entries.append(entry)

    # Clean up examples
    for entry in entries:
        for sense in entry["senses"]:
            sense["examples"] = [ex.replace("|", "").strip() for ex in sense["examples"]]

    return entries

if __name__ == "__main__":
    
    entries = extract_hanzi_cihui_entries(html)

    # Print results
    for entry in entries:
        print(f"Hanzi: {entry['hanzi']}")
        print(f"Pinyin: {entry['pinyin']}")
        if 'words' in entry:
            print(f"Words: {entry['words']}")
        for sense in entry["senses"]:
            print(f"  Part of Speech: {sense['pos']}")
            print(f"  Definition: {sense['definition']}")
            print(f"  Examples: {sense['examples']}")
        print("="*40)