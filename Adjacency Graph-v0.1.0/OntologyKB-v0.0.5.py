# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:59:14 2019
Last modified on Oct. 7 10:07 2019
@author: 
"""
"""
Ontology based adjacency graph 

"""
import sys
sys.path.append('./HandDetection')
sys.path.append('./SpeechRec')
import threading
import argparse
import re
import os
import cv2
import Brain as KB # KB framework
import InteractiveSession as sess
import Recognizer

# Global variables
parser = argparse.ArgumentParser()
parser.add_argument("--kbpath",
                    help="The path where a previous KB was stored.",
                    default='E:\\Research')
# parser.add_argument("--imgpath",
#                     help="The path where images were stored.")
args = parser.parse_args()

cur_gpath=args.kbpath # The file where knowledge graphs are stored
object_list=[]
g=KB.Graph(directed=True)
count = 0
hd=[]
cur_frame=[]
handPosition=0
x =[]

# Abort the whole program
close_flag = False

# flags used for action recording
actionVideo=[]
video_name = ' '
record_start_flag = False
record_stop_flag = False
record_flag = False
def test():
    global hd
    # while True:
    #     hd.detectHand()
    #     if cv2.waitKey(10) == 'q':
    #         break


def testThreading():
    global g, cur_frame, hd, handPosition, close_flag, record_start_flag, \
    record_stop_flag, record_flag, video_name, actionVideo

    tool = []
    vertex = []
    process_finish = 0
    process = KB.Graph(directed=True)

    while True:
        if record_stop_flag:
            continue
        if process_finish==1:
            process=KB.Graph(directed=True)
            process_finish=0

        order = (input('\033[1;33;0m Waiting for orders... \033[0m')).lower()
        # Learn a new vertex of knowledge
        match = re.match('this object is', order)
        if match is not None:
            # Describe this object
            state = []
            contents = []
            category = None
            name = order[15:]

            while True:
                # requiring...
                description = input('\033[1;33;0m Please decribe it... \033[0m').lower()

                # Speech Recognition Here!
                # Say 'ok' to finish the description of this object
                prop = re.match('ok', description)
                if prop is not None:
                    break

                # Say 'category' to specify its category
                prop = re.match('category', description)
                if prop is not None:
                    category = description[9:]
                    continue

                # Say 'contents' to describe the stuff in it
                prop1 = re.match('contents', description)
                prop2 = re.match('content', description)
                if prop1 is not None or prop2 is not None:
                    contents = description.split()
                    contents = contents[1:]
                    continue

                # Say 'state' to describe the features of the object
                prop1 = re.match('state', description)
                prop2 = re.match('states', description)
                if prop1 is not None or prop2 is not None:
                    while 1:
                        # Requiring...
                        s = input('\033[1;33;0m Please describe its state... \033[0m').lower()

                        # Speech Recognition Here!
                        # Say something that describes the properties of the object
                        # Say 'done' to stop this procedure
                        if re.match('done', s):
                            break
                            # Describe relation between this object and other objects that have been learned
                            # Preposition relation: on, in, under, next
                            # incomplete...

                        state.append(s)

                    continue

            vertex = KB.Vertex(name=name, state=state, contents=contents, category=category)
            process.insert_vertex(vertex)


            # Take photo
            object_pos = handPosition[0]
            cv2.waitKey(2000) # Please move your hands away from the object

            object_img = hd.img.src[object_pos[1]:object_pos[1]+object_pos[3], \
                         object_pos[0]:object_pos[0]+object_pos[2],:]

            img_path = cur_gpath + '\\' +g.title+ '\\Objects\\' + name
            for i in range(len(state)):
                img_path=img_path+'_'+state[i]
            img_path+='.jpg'

            cv2.imwrite(img_path, object_img)


        # Learning tool objects
        match = re.match('this tool is', order)
        if match is not None:
            tool = KB.Vertex(name=order[13:], category='tool',state=['clean'])
            process.insert_vertex(tool)

            # Take photo
            tool_pos = handPosition[0]
            cv2.waitKey(2000)  # Please move your hands away from the object
            tool_img = hd.img.src[tool_pos[1]:tool_pos[1] + tool_pos[3], \
                         tool_pos[0]:tool_pos[0] + tool_pos[2], :]
            img_path = cur_gpath + '\\' + g.title + '\\Objects\\' + tool._name + '.jpg'

            cv2.imwrite(img_path, tool_img)


        match = re.match('save',order)
        if match is not None:
            KB.save_KB(g,cur_gpath + '\\' + g.title + '\\' + g.title + '.kb')

        match = re.match('display',order)
        if match is not None:
            print('\033[22;34;0m')
            print(g)
            g.display_processes()
            print('\033[0m')

        match = re.match('quit',order)
        if match is not None:
            KB.save_KB(g,cur_gpath + '\\' + g.title + '\\' + g.title + '.kb')
            close_flag = True
            print('save and quit')
            hd.out.release()
            hd.img.cap.release()
            break


        match = re.match('we',order)
        if match is not None:
            process_finish=1
            # ex: we use knife to cut apple, and get apple slices


            #Extrcat action
            spacelist = [i.start() for i in re.finditer(' ', order)]
            actionLocStart = spacelist[3]
            actionLocEnd = spacelist[4]
            action_name = order[actionLocStart+1:actionLocEnd]

            video_name = cur_gpath + '\\' + g.title + '\\Motions\\' + action_name + '.avi'
            record_start_flag = True
            while True:
                command  = (input("\033[1;33;0m Say 'finish' to end recording... \033[0m")).lower()
                # Speech Recognition
                match = re.match('finish', command)
                if match is not None:
                    record_stop_flag = True
                    break

            action = KB.Vertex(name=action_name, state=None, contents=None, category='Motion')
            process.insert_vertex(action)

            #Extract result
            result=re.search('get',order)
            result=result.span()
            result=order[result[1]+1:]
            result=KB.Vertex(name=result, category=vertex._category,state=['be '+action._name])
            process.insert_vertex(result)

            process.insert_incident_edge(vertex,action)
            process.insert_incident_edge(tool,action)
            process.insert_incident_edge(action,result)

            g.add_process([process])
            print(g.vertex_count())
            print(tool)
            print(vertex)
            g.display_processes()

def initSession():
    """ Activate and Initialize a interaction session with ontology knowledge base. """
    global hd, out
    hd = Recognizer.handDetector(0)
    hd.initDetector()

    while True:
        order = (input('\033[1;33;0m Please select a scenario... \033[0m')).lower()
        global g
        # New knowledge base
        match = re.match('new', order)
        if match is not None:
            title = order[4:]
            if len(title) == 0:  # If title was not specified, it will be specified as current local time
                title = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            try:
                g = KB.Graph(title=title, directed=True)
                filename = cur_gpath + '\\' + title
                os.mkdir(filename)
                filename = cur_gpath + '\\' + title + '\\Objects'
                os.mkdir(filename)
                filename = cur_gpath + '\\' + title + '\\Motions'
                os.mkdir(filename)
                filename = cur_gpath + '\\' + title + '\\' + title + '.kb'
                KB.save_KB(g, filename)
                print("\033[1;34m Knowledge base opened successfully... \033[0m")
                print('\033[1;34m <--------------------------', g.title, '--------------------------> \033[0m')
                return
            except:
                ans = (input('\033[1;33;0m Knowledge base has existed, do you want to load it? (Y/N) \033[0m')).lower()
                if ans=='y' or ans=='yes':
                    g=KB.load_KB(cur_gpath + '\\' + order[4:] + '\\' + order[4:] + '.kb')
                    print("\033[1;34;0m Knowledge base opened successfully... \033[0m")
                    print('\033[1;34;0m <--------------------------', g.title, '--------------------------> \033[0m')
                elif ans=='n' or ans=='no':
                    continue
                return

        # Open an existing knowledge base
        match = re.match('open', order)
        if match is not None:
            g = KB.load_KB(cur_gpath + '\\' + order[5:] + '\\' + order[5:] + '.KB')
            print("\033[1;34;0m Knowledge base opened successfully... \033[0m")
            print('\033[1;34;0m <--------------------------', g.title, '--------------------------> \033[0m')
            return

        print('\033[0;31m Order cannot be identified... \033[0m')

def interactiveSession():
    """Interacting with ontology knowledge base.

        Users can instruct knowledge base to:
        1) Recognize and then learn objects in the given scenario;
        2) Record and then recognize actions;
        3) Organize object vertices and action vertices as a directed graph according to 
        the logical and temporal relation entailed in instructional speech;
        4) Load or store a graph as binary file(*.kb).
       """
    global handPosition, out, x, close_flag, record_start_flag, record_stop_flag, video_name, \
    actionVideo, record_flag


    x = threading.Thread(target=testThreading, args=())
    x.start()

    while close_flag == False:
        handPosition = hd.detectHand()

        # Start to record action
        if record_start_flag:
            print('Start recording action...\n The video path is '+video_name)
            actionVideo = cv2.VideoWriter(
                filename=video_name,
                fourcc=cv2.VideoWriter_fourcc(*'XVID'),
                fps=20,
                frameSize=(640, 480),
                isColor=1)
            record_start_flag = False
            record_flag = True

        # Stop recording action
        if record_stop_flag:
            print('Saving action video, please wait... ')
            actionVideo.release()
            record_flag = False
            record_stop_flag = False



        if record_flag:
            actionVideo.write(hd.img.plainImg)

        hd.out.write(hd.img.src)
        if cv2.waitKey(10) == 'q':
            break
    cv2.destroyAllWindows()

    return
# Activate session


initSession()
interactiveSession()






    # while (1):
#     option = input("请输入所要执行的操作的编号\n0:建立新知识图谱 1:输入图像信息 2:输入视频信息 3:输入语音信息")
#
#     if option == '1':
#         capture = cv2.VideoCapture(1)
#         ret, frame = capture.read()
#         img_path = 'E:\\Research\\' + str(count) + '.jpg'
#         cv2.imwrite(img_path, frame)
#         cv2.imshow('img', frame)
#         img = image.load_img(img_path, target_size=(224, 224))
#         x = image.img_to_array(img)
#         x = np.expand_dims(x, axis=0)
#         x = resnet50.preprocess_input(x)
#
#         preds = model.predict(x)
#         result = resnet50.decode_predictions(preds, top=1)[0][0][1]
#
#         v = Vertex(1, result, ['Unchopped'], None, 'Fruit', img_path)
#         print(v)
#         G.insert_vertex(v)


#----------------------------------------------------------------------------
#
