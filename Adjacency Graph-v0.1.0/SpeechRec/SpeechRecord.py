import logging
import threading
import time
import pyaudio
import wave
import cv2
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "test.wav"

mag=[]

def initAudio():
    global p, inputStream
    p = pyaudio.PyAudio()
    inputStream = p.open(format=FORMAT,
                         channels=CHANNELS,
                         rate=RATE,
                         input=True,
                         frames_per_buffer=CHUNK)


def speechRecording():
    global p, inputStream
    print("Please say something...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = inputStream.read(CHUNK)
        frames.append(data)

    print("End recording...!")

    inputStream.stop_stream()
    inputStream.close()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    p.terminate()



def playAudio():
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'rb')

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data
    data = wf.readframes(CHUNK)

    # play stream (3)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    # close PyAudio (5)
    p.terminate()

def thread_function():

    logging.info("Thread : starting")

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Please say something...")

    frames = []

    global mag

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        audio_data = np.fromstring(data, dtype=np.short)
        mag.append(np.max(audio_data))
        frames.append(data)

    print("End recording...!")


    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


    #playAudio()
    logging.info("Thread : finishing")



if __name__ == "__main__":

    format = "%(asctime)s: %(message)s"

    logging.basicConfig(format=format, level=logging.INFO,

                        datefmt="%H:%M:%S")


    logging.info("Main : before creating thread")

    x = threading.Thread(target=thread_function, args=())

    logging.info("Main : before running thread")

    x.start()

    t=time.clock()
    cap=cv2.VideoCapture(0)
    while time.clock()-t<10:
        print(time.clock())
        _,frame=cap.read()
        cv2.imshow("f",frame)
        cv2.waitKey(5)


    # x.join()

    logging.info("Main : all done")


    #global mag
    tt = np.array([i for i in range(len(mag))])
    mag = np.array(mag)

    plt.plot(tt, mag)
    plt.show()
    #playAudio()







