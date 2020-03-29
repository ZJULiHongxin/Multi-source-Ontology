# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:59:14 2019
Last modified on Jan. 27th 10:07 2020
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
import shutil
import Brain as KB # KB framework
import InteractiveSession as sess
import Recognizer
from SpeechRecognition import *


parser = argparse.ArgumentParser()
parser.add_argument("--kbpath",
                    help="The path where a previous KB was stored.",
                    default='./')
# parser.add_argument("--imgpath",
#                     help="The path where images were stored.")
args = parser.parse_args()

class KnowledgeGraph:
    __slots__="KBpath","g","hd","cur_frame","handPosition","x",\
    "close_flag","actionVideo","video_name","record_start_flag",\
    "record_stop_flag","record_flag","mode","ARGS","model"

    def __init__(self, KBpath):

        self.KBpath=KBpath
        self.g = KB.Graph(directed=True)

        # Abort the whole program
        self.close_flag = False

        # flags used for action recording
        self.actionVideo = []
        self.video_name = ' '
        self.record_start_flag = False
        self.record_stop_flag = False
        self.record_flag = False

        print('\033[1;33;0m Initializing hand detector. Please cover the squares with your hands... \033[0m')
        self.hd = Recognizer.handDetector(0)
        self.hd.initDetector()
        self.cur_frame=[]
        self.handPosition=0
        self.x =[]


        # mode = (input("Use voice?(Y/N)")).upper()
        self.mode = 'N'
        if self.mode == 'Y':
            # SpeechRecognizer initialization
            self.ARGS, self.model = init_Speechrec()


    def initSession(self):
        """ Activate and Initialize a interaction session with ontology knowledge base. """


        while True:
            print("\033[1;33;0m Please select a scenario ... \n ( Say 'new kitchen' to new a knowledge base for kitchen situation)\n ( Say 'open kitchen' to open a existing knowledge base)\n  \033[0m")
            if self.mode == 'Y':
                order = (input_voice_secure(ARGS, model, "waiting for order...")).lower()
            else:
                order = (input("waiting for order...")).lower()

            # New knowledge base
            match = re.match('new', order)
            if match is not None:
                title = order[4:]
                while True:
                    if len(title) == 0:  # If title was not specified, it will be specified as current local time
                        title = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    try:
                        self.g.title=title
                        filename = self.KBpath + '\\' + title
                        os.mkdir(filename)
                        filename = self.KBpath + '\\' + title + '\\Objects'
                        os.mkdir(filename)
                        filename = self.KBpath + '\\' + title + '\\Motions'
                        os.mkdir(filename)
                        filename = self.KBpath + '\\' + title + '\\' + title + '.kb'
                        KB.save_KB(self.g, filename)
                        print("\033[1;34m Knowledge base opened successfully... \033[0m")
                        print('\033[1;34m <--------------------------', self.g.title, '--------------------------> \033[0m')
                        return

                    except FileExistsError:
                        ans = (input('\033[1;33;0m Knowledge base has existed, do you want to load it? (Y/N) \033[0m')).lower()
                        if ans=='y' or ans=='yes':
                            self.g=KB.load_KB(self.KBpath + '\\' + order[4:] + '\\' + order[4:] + '.kb')
                            print("\033[1;34;0m Knowledge base opened successfully... \033[0m")
                            print('\033[1;34;0m <--------------------------', self.g.title, '--------------------------> \033[0m')
                        elif ans=='n' or ans=='no':
                            ans = input(('\033[1;33;0m Delete the existed one and create a new base? (Y/N) \033[0m')).lower()
                            if ans == 'y' or ans == 'yes':
                                shutil.rmtree((KBpath + '\\' + title))
                                print("\033[1;34m Knowledge base deleted successfully... \033[0m")
                            continue

            # Open an existing knowledge base
            match = re.match('open', order)
            if match is not None:
                self.g = KB.load_KB(self.KBpath + '\\' + order[5:] + '\\' + order[5:] + '.KB')
                print("\033[1;34;0m Knowledge base opened successfully... \033[0m")
                print('\033[1;34;0m <--------------------------', self.g.title, '--------------------------> \033[0m')
                return

            print('\033[0;31m Order cannot be identified... \033[0m')

    def interactiveSession(self):
        """Interacting with ontology knowledge base.
    
            Users can instruct knowledge base to:
            1) Recognize and then learn objects in the given scenario;
            2) Record and then recognize actions;
            3) Organize object vertices and action vertices as a directed graph according to 
            the logical and temporal relation entailed in instructional speech;
            4) Load or store a graph as binary file(*.kb).
           """

        self.x = threading.Thread(target=self.testThreading, args=())
        self.x.start()

        while self.close_flag == False:
            self.handPosition = self.hd.detectHand()

            # Start to record action
            if self.record_start_flag:
                print('Start recording action...\n The video path is '+self.video_name)
                self.actionVideo = cv2.VideoWriter(
                    filename=self.video_name,
                    fourcc=cv2.VideoWriter_fourcc(*'XVID'),
                    fps=20,
                    frameSize=(640, 480),
                    isColor=1)
                self.record_start_flag = False
                self.record_flag = True

            # Stop recording action
            if self.record_stop_flag:
                print('Saving action video, please wait... ')
                self.actionVideo.release()
                self.record_flag = False
                self.record_stop_flag = False

            if self.record_flag:
                self.actionVideo.write(self.hd.img.plainImg)

            self.hd.out.write(self.hd.img.src)
            if cv2.waitKey(10) == 'q':
                break
        cv2.destroyAllWindows()

        return

    def testThreading(self):

        tool = []
        vertex = []
        process_finish = 0
        process = KB.Graph(directed=True)

        while True:
            if self.record_stop_flag:
                continue
            if process_finish == 1:
                process = KB.Graph(directed=True)
                process_finish = 0
            print("""\033[1;33;0m Describe a process: 
    - say 'this object is apple' to create a object vertex in the graph 
    - say 'this tool is knife' to create a tool vertex in the graph 
    - say 'we use knife to cut apple, and get apple slices' to record the  
    action implemented later on 
    \033[0m""")

            if self.mode == 'N':
                order = (input('Waiting for order...')).lower()
            else:
                order = (input_voice_secure(self.ARGS, self.model, 'Waiting for order...')).lower()
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
                    if self.mode == 'N':
                        description = input('\033[1;33;0m Please decribe it... \033[0m').lower()
                        prop = re.match('ok', description)
                        if prop is not None:
                            break
                    else:
                        # Speech Recognition Here!
                        # Say 'okay' to finish the description of this object
                        description = (input_voice_secure(self.ARGS, self.model, \
                                      '\033[1;33;0m Please decribe it... \033[0m')).lower()
                        if re.match('okay', description):
                            break
                    # Say 'category' to specify its category
                    prop = re.match('category', description)
                    if prop is not None:
                        print("category updated:")
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
                            if self.mode == 'N':
                                s = input('\033[1;33;0m Please describe its state... \033[0m').lower()
                            else:
                                # Speech Recognition Here!
                                # Say something that describes the properties of the object
                                # Say 'done' to stop this procedure
                                s_single = (input_voice_secure(self.ARGS, self.model,
                                                               '\033[1;33;0m Please describe its state... \033[0m')).lower()
                                while not description_single == 'done':
                                    s = s + '.' + s_single
                                    s_single = (input_voice(ARGS, model)).lower()
                                break
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
                object_pos = self.handPosition[0]
                print('The program will take a photo in 2 seconds, please move away your hands...')
                cv2.waitKey(2000)  # Please move your hands away from the object

                object_img = self.hd.img.src[object_pos[1]:object_pos[1] + object_pos[3], \
                             object_pos[0]:object_pos[0] + object_pos[2], :]

                img_path = self.KBpath + '\\' + self.g.title + '\\Objects\\' + name
                for i in range(len(state)):
                    img_path = img_path + '_' + state[i]
                img_path += '.jpg'

                cv2.imwrite(img_path, object_img)

            # Learning tool objects
            match = re.match('this tool is', order)
            if match is not None:
                tool = KB.Vertex(name=order[13:], category='tool', state=['clean'])
                process.insert_vertex(tool)

                # Take photo
                tool_pos = self.handPosition[0]
                print('The program will take a photo in 2 seconds, please move away your hands...')
                cv2.waitKey(2000)  # Please move your hands away from the object
                tool_img = self.hd.img.src[tool_pos[1]:tool_pos[1] + tool_pos[3], \
                           tool_pos[0]:tool_pos[0] + tool_pos[2], :]
                img_path = self.KBpath + '\\' + self.g.title + '\\Objects\\' + tool._name + '.jpg'

                cv2.imwrite(img_path, tool_img)

            match = re.match('save', order)
            if match is not None:
                KB.save_KB(self.g, self.KBpath + '\\' + self.g.title + '\\' + self.g.title + '.kb')

            match = re.match('display', order)
            if match is not None:
                print('\033[22;34;0m')
                print(self.g.vertex_count())
                self.g.display_processes()
                print('\033[0m')

            match = re.match('quit', order)
            if match is not None:
                KB.save_KB(self.g, self.KBpath + '\\' + self.g.title + '\\' + self.g.title + '.kb')
                close_flag = True
                print('save and quit')
                self.hd.out.release()
                self.hd.img.cap.release()
                break

            match = re.match('we', order)
            if match is not None:
                process_finish = 1
                # ex: we use knife to cut apple, and get apple slices


                # Extrcat action
                spacelist = [i.start() for i in re.finditer(' ', order)]
                actionLocStart = spacelist[3]
                actionLocEnd = spacelist[4]
                action_name = order[actionLocStart + 1:actionLocEnd]

                self.video_name = self.KBpath + '\\' + self.g.title + '\\Motions\\' + action_name + '.avi'
                self.record_start_flag = True
                while True:
                    command = (input("\033[1;33;0m Say 'finish' to end recording... \033[0m")).lower()
                    # Speech Recognition
                    match = re.match('finish', command)
                    if match is not None:
                        self.record_stop_flag = True
                        break

                action = KB.Vertex(name=action_name, state=None, contents=None, category='Motion')
                process.insert_vertex(action)

                # Extract result
                result = re.search('get', order)
                result = result.span()
                result = order[result[1] + 1:]
                result = KB.Vertex(name=result, category=vertex._category, state=['be ' + action._name])
                process.insert_vertex(result)

                process.insert_incident_edge(vertex, action)
                process.insert_incident_edge(tool, action)
                process.insert_incident_edge(action, result)

                self.g.add_process([process])
                print(tool)
                print(vertex)
                print(action)
                print(result)
                self.g.display_processes()
# Activate session

testG=KnowledgeGraph(args.kbpath)
testG.initSession()
testG.interactiveSession()
#testThreading()
