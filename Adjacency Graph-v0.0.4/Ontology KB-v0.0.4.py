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
sys.path.append('E:\\github\Multi-source-Ontology\\Adjacency Graph-v0.0.4\\HandDetection')
sys.path.append('E:\\github\Multi-source-Ontology\\Adjacency Graph-v0.0.4\\SpeechRec')
import threading
import argparse
import re
import os
import cv2
import Brain as KB # KB framework
import InteractiveSession as sess
import Recognizer

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
process=KB.Graph(directed=True)
capture = cv2.VideoCapture(0)
count = 0
def testThreading():
    print('Test')

def activateSession():
    """ Activate and Initialize a interaction session with ontology knowledge base. """
    global capture
    while (1):
        print('Program activated...')

        try:
            capture = cv2.VideoCapture(1)
        except:
            print('Webcam open failure, find another one!')
            try:
                capture = cv2.VideoCapture(0)
            except:
                print('Webcam open failure!')
            exit(0)
        break;


    while (1):
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
    global g
    global capture
    global process
    tool=[]
    vertex=[]
    process_finish=0


    while True:
        if process_finish==1:
            process=KB.Graph(directed=True)
            process_finish=0
        handPosition = hd.detectHand()

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
                    state = []
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
            ret, frame = capture.read()
            img_path = cur_gpath + '\\' +g.title+ '\\Objects\\' + name
            for i in range(len(state)):
                img_path=img_path+'_'+state[i]
            img_path+='.jpg'

            cv2.imwrite(img_path, frame)
            cv2.imshow('img', frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Learning tool objects
        match = re.match('this tool is', order)
        if match is not None:
            tool = KB.Vertex(name=order[13:], category='tool',state=['clean'])
            process.insert_vertex(tool)

            # Take photo
            ret, frame = capture.read()
            img_path = cur_gpath + '\\' + g.title + '\\Objects\\' + tool._name
            img_path += '.jpg'

            cv2.imwrite(img_path, frame)
            cv2.imshow('img', frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            pass

        match = re.match('save',order)
        if match is not None:
            KB.save_KB(g,cur_gpath + '\\' + g.title + '\\' + g.title + '.kb')

        match = re.match('display',order)
        if match is not None:
            print('\033[22;34;0m')
            print(g)
            g.display_processes()
            print('\033[0m')

        match = re.match('we',order)
        if match is not None:
            process_finish=1
            # we use knife to cut apple, and get apple slices

            #Extrcat action
            spacelist = [i.start() for i in re.finditer(' ', order)]
            actionLocStart = spacelist[3]
            actionLocEnd = spacelist[4]
            action = order[actionLocStart:actionLocEnd]
            action = KB.Vertex(name=action, state=None, contents=None, category='Motion')
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


    return
# Activate session


activateSession()
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
