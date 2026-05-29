import json
from bs4 import BeautifulSoup

file_name = 'xdhy_entries'
entry_key = "entry"
result_name = "xdhy_entries_parsed"

def get_chinese_example(current_element, show_log=False):
  # 初始化中文例子
  chinese_example = ''
  while current_element:
      if(show_log):
        print(f"get_chinese_example:{current_element=}")
      if current_element.name == 'span' and 'en' in current_element.get('class', []):
        break
      # 如果当前节点是字符串，即纯文本节点
      if isinstance(current_element, str):
          chinese_example += current_element.strip()
      else:
          # 如果当前节点是元素节点
          if current_element.name == 'span' and \
           ('shuxian' not in current_element.get('class', []) and 'maohao' not in current_element.get('class', [])):
              # 获取元素节点的文本内容
              chinese_example += current_element.get_text(strip=True)
          # 如果当前节点不是 <span> 标签，可能是其他元素，按需要处理

      # 查找下一个兄弟节点
      current_element = current_element.next_sibling
  return chinese_example, current_element


def parseContentCase1for3(html_content, show_log = False):
  soup = BeautifulSoup(html_content, 'html.parser')

  word = soup.find('span', class_='hw').find('word').text
  pinyinParent = soup.find('span', class_='pinyin')
  cn = None
  if pinyinParent is None:
    explain_tag = soup.find('explain')
    pinyin = ''
    pinyinParent = explain_tag.next_element
    # print("explain_tag.text:", pinyinParent)
    if explain_tag:
      pinyin = pinyinParent.split('\n')[0].strip()  # 拼音通常是解释的第一行
      cn = pinyinParent.split('\n')[1].strip()

  else:
    pinyin = pinyinParent.find('pinyin').text

  definitions = soup.find_all('span', class_='num')

  # Prepare data for JSON
  data = {}
  data[word] = {
      'pinyin': pinyin,
      'definitions': []
  }


  def process_definition(num, single=False, cn = None):
    definition_num = num.text.strip() if not single else '1.'
    definition_text = ''
    definition_english = ''
    examples_chinese = []
    examples_english = []

    # Extract Chinese definition
    # chinese_text = num.find_next_sibling(text=True)
    chinese_text, english_span = get_chinese_example(num.next_sibling)
    if chinese_text:
        definition_text = chinese_text.strip()
    else:
        definition_text = cn

    # Extract English definition
    # english_span = num.find_next('span', class_='en')
    current_element = None
    if english_span:
        definition_english = english_span.get_text(strip=True)
        definition_english = definition_english.replace('{', '').replace('}', '')


        # Find all related examples
        # current_element = english_span.find_next_sibling()
        current_element = english_span.find_next('span', class_='maohao')


    while current_element:
        if(show_log):
          print(f"{current_element=}")

        if current_element.name == 'span' and \
         ('shuxian' in current_element.get('class', []) or \
          'maohao' in current_element.get('class', [])):
            current_element = current_element.next_sibling
            continue
        if current_element.name == 'span' and 'en' in current_element.get('class', []):
            example_english = current_element.get_text(strip=True).replace('{', '').replace('}', '')
            examples_english.append(example_english)
            current_element = current_element.find_next_sibling()
        else:
            example_text, current_element = get_chinese_example(current_element, show_log)
            examples_chinese.append(example_text)

        if current_element and current_element.name == 'br':
            break

        # Append data for each example
    data[word]['definitions'].append({
        'num': definition_num,
        'cn': definition_text,
        'en': definition_english,
        'ex_cn': examples_chinese,
        'ex_en': examples_english
    })

  if len(definitions) > 0:
    for num in definitions:
      process_definition(num)
  else:
    process_definition(pinyinParent,single=True, cn=cn)

  return data


if __name__ == "__main__":
    json_file = f'raw_data/{file_name}.json'
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    phrase_array = []

    fail_phrases_n = 0
    n = 0
    for item in data:
        entry_value = item[entry_key]
        paraphrase = item['paraphrase']
        n += 1
        entry_phrases = []
        print(f"Processing {entry_value}")
        try:
            phrase_json = parseContentCase1for3(paraphrase)
            # get the pharase_json' entry values
            entry_phrases.append(list(phrase_json.values())[0])
        except Exception as e:
            fail_phrases_n += 1
            print(f"Error processing {entry_value}#{n}: {e}")
            print(paraphrase)

        phrase_array.append({entry_value: entry_phrases})

    print("Entry size:", len(data))
    print("Total phrases length:", len(phrase_array))
    print("Failed phrases length:", fail_phrases_n)
    # Write data to JSON
    with open(f'raw_data/{result_name}.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(phrase_array, jsonfile, ensure_ascii=False, indent=4)