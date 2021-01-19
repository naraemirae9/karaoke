import pyaudio
import numpy as np
import wave, os
from datetime import datetime
from audioop import mul, add, bias

INPUT_INDEX = 2
OUTPUT_INDEX = 3
OUTPUT_FILENAME = 'output/%s.wav' % (datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.makedirs('output', exist_ok=True)

CHUNK = 512  #한번에 받을 수 있는 스트림의 양
RATE = 48000
SAMPLE_WIDTH = 2
DELAY_INTERVAL = 15 #delay
DELAY_VOULUME_DECAY = 0.6 #delay 뒤에 오는 소리 크기
DELAY_N = 10

original_frames =[]
index = 0

def add_delay(input):
    global original_frames, index

    original_frames.append(input)
    output = input

    if len(original_frames) > DELAY_INTERVAL:
        for n_repeat in range(DELAY_N):
            delay = original_frames[max(index - n_repeat * DELAY_INTERVAL, 0)]

            delay = mul(delay, SAMPLE_WIDTH, DELAY_VOULUME_DECAY ** (n_repeat + 1))
            output = add(output, delay, SAMPLE_WIDTH)

        index +=1
    
    return output
    

def start_stream():
    stream =pa.open(
        format = pyaudio.paInt16,
        channels=1,
        rate =RATE,
        frames_per_buffer=CHUNK,
        input=True,
        output=True,
        input_device_index=INPUT_INDEX,
        output_device_index=OUTPUT_INDEX
    )

    frames =[]

    #start strema
    while stream.is_active():
        try:
            input = stream.read(CHUNK, exception_on_overflow=False)
            input = add_delay(input)  #주석처리하면 그대로 나옴

            stream.write(input)
            frames.append(input)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print('[!] Unknown error!',e)
            exit()

    #파일로 저장
    total_frames = b''.join(frames)

    with wave.open(OUTPUT_FILENAME, 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
        f.setframerate(RATE)
        f.writeframes(total_frames)

    stream.stop_stream()
    stream.close()
    pa.terminate()



#main
pa =pyaudio.PyAudio()

for i in range(pa.get_device_count()):
    print(pa.get_device_info_by_index(i))


start_stream()