# coding=utf-8
import os
from dotenv import load_dotenv
load_dotenv()

import sys
import csv
from dashscope.audio.tts import SpeechSynthesizer
import dashscope
import time

dashscope.api_key = os.getenv('MODEL_API_KEY', 'not-needed')

csv_path = 'database_csv/hanzi_definition_v7_with_pos_updated.csv'
output_dir = 'voice_data/definition_files'
os.makedirs(output_dir, exist_ok=True)

def synthesize_and_save(definition_id, definition_cn):
    try:
        result = SpeechSynthesizer.call(
            model='sambert-zhiye-v1',
            text=definition_cn,
            sample_rate=48000,
            volume=100,
            rate=0.8,
            format='mp3'
        )
        if result.get_audio_data() is not None:
            out_path = os.path.join(output_dir, f'defid_{definition_id}.mp3')
            with open(out_path, 'wb') as f:
                f.write(result.get_audio_data())
            print(f'SUCCESS: {definition_id} ({definition_cn[:10]}...)')
        else:
            print(f'ERROR: {definition_id} ({definition_cn[:10]}...): {result.get_response()}')
    except Exception as e:
        print(f'EXCEPTION: {definition_id} ({definition_cn[:10]}...): {e}')

with open(csv_path, encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    rows = list(reader)
    total = len(rows)
    print(f'Total lines to be processed: {total}')
    for i, row in enumerate(rows, 1):
        definition_id = row['definition_id']
        definition_cn = row['definition_cn']
        print(f'Processing {i}/{len(rows)}', end='->')
        if not definition_cn.strip():
            print(f'SKIP (empty): {definition_id}')
            continue
        out_path = os.path.join(output_dir, f'defid_{definition_id}.mp3')
        if os.path.exists(out_path):
            print(f'SKIP (exists): {definition_id}')
            continue
        synthesize_and_save(definition_id, definition_cn)
        # time.sleep(0.5)  # avoid rate limits