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
sys.path.append('./ImageRecognition')
import threading
import argparse
import traceback
import pickle
import re
import os
import cv2
import shutil
import networkx as nx
import matplotlib.pyplot as plt
import Recognizer
import Vision
from SpeechRecognition import *

parser = argparse.ArgumentParser()
parser.add_argument("--kbpath",
                    help="The path where a previous KB was stored.",
                    default='./')
# parser.add_argument("--imgpath",
#                     help="The path where images were stored.")
args = parser.parse_args()


class Vertex:
    """ Vertex structure for a graph
    @ Members: 'name'
               'state': A list storing previous and current states of this object
               'content': A set storing contents of this object if it is not a type of motion
               'category': category this object belongs to
               'img_path': file path where storing images of this object 
    """

    __slots__ = 'element', 'name', 'state', 'contents', 'category', 'img_path'

    def __init__(self, x=-1, name='', state=None, contents=None, category='', imgpath=None):
        self.element = x
        self.name = name

        if state is None:
            self.state = ['']
        else:
            self.state = state

        if contents is None:
            self.contents = ['']
        else:
            self.contents = contents

        self.category = category

        if imgpath is None:
            self.img_path = []
        else:
            self.img_path = imgpath

    def get_element(self):
        """Return element associated with this vertex"""
        return self.element

    def set_img_path(self, path):
        self.img_path = path

    def get_img_path(self):
        return self.img_path

    def __str__(self):
        string = '+ ' + '- ' * 20 + '+' + '\n'
        string += '|' + 15 * ' ' + 'Object Node' + 15 * ' ' + '|' + '\n'
        string += '| ' + 'Object name: ' + self.name + (27 - len(self.name)) * ' ' + '|' + '\n'
        if self.category != '':
            string += '| ' + 'Object category: ' + self.category + (23 - len(self.category)) * ' ' + '|' + '\n'
        else:
            string += '| ' + 'Object category: ' + 'None' + 19 * ' ' + '|' + '\n'

        substring1 = ''
        if len(self.state) != 0:
            string += '| ' + 'Object current state: ' + self.state[-1] + (18 - len(self.state[-1])) * ' ' + '|' + '\n'
            if len(self.state) >= 1:
                for i in range(len(self.state) - 1):
                    substring1 += '| ' + 'Object history state {}'.format(i) + ': ' + self.state[i] + (16 - len(
                        self.state[i])) * ' ' + '|' + '\n'

        string += substring1
        substring2 = ''
        if self.contents != '':
            for i in range(len(self.contents)):
                substring2 += '| ' + 'Object contents: ' + self.contents[i] + (23 - len(
                    self.contents[i])) * ' ' + '|' + '\n'
        else:
            substring2 = '| ' + 'Object contents: None' + 19 * ' ' + '|' + '\n'

        string += substring2
        string += '+ ' + '- ' * 20 + '+' + '\n'

        return string

    def __hash__(self):  # Allow vertex to be a map/set key
        return hash(id(self))

    def __eq__(self, other):
        return self.name == other.name \
               and self.state == other.state \
               and self.contents == other.contents \
               and self.category == other.category \
               and self.img_path == other.img_path


class KnowledgeGraph:
    __slots__ = "KBpath", "g", "hd", "cur_frame", "handPosition", "x", "graphics", \
                "close_flag", "actionVideo", "video_name", "record_start_flag", \
                "record_stop_flag", "record_flag", "mode", "ARGS", "model", "title", \
                "IR", "val_map", "draw_graph_flag"

    def __init__(self, KBpath):

        self.KBpath = KBpath
        self.g = None
        self.title = ''

        # Abort the whole program
        self.close_flag = False

        # flags used for action recording
        self.actionVideo = []
        self.video_name = ' '
        self.record_start_flag = False
        self.record_stop_flag = False
        self.record_flag = False
        self.draw_graph_flag = False

        print('\033[1;33;0m Initializing hand detector. Please cover the squares with your hands... \033[0m')
        self.hd = Recognizer.handDetector(0, 1)
        self.hd.initDetector()
        self.cur_frame = []
        self.handPosition = 0

        self.val_map = {'Tool': 1.0, 'Motion': 0.8, 'Fruit': 0.3, 'Sauce': 0.4, '': 0.5}

        # mode = (input("Use voice?(Y/N)")).upper()
        self.mode = 'N'
        if self.mode == 'Y':
            # SpeechRecognizer initialization
            self.ARGS, self.model = init_Speechrec()

    def initSession(self):
        """ Activate and Initialize a interaction session with ontology knowledge base. """
        while True:
            # Enquiring...
            print(
                "\033[1;33;0m Please select a scenario ... \n ( Say 'new kitchen' to new a knowledge base for kitchen situation)\n ( Say 'open kitchen' to open a existing knowledge base)\n  \033[0m")
            if self.mode == 'Y':
                order = (input_voice_secure(ARGS, model, "waiting for order...")).lower()
            else:
                order = (input("waiting for order...")).lower()

            # Create a new knowledge base
            match = re.match('new', order)
            if match is not None:
                title = order[4:]
                self.title = title
                if len(title) == 0:  # If title was not specified, it will be specified as current local time
                    title = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                filep = os.path.join(self.KBpath, title)
                print('\033[1;33m [Note] The path: \033[0m', end='')
                print(filep)
                create_flag = True

                if os.path.exists(filep):
                    print("\033[1;31m Knowledge base " + title + " already exists! \033[0m")
                    print("\033[1;33m Would you like to delete the existing KB and create a new one? [Y/N] \033[0m")
                    print(
                        "\033[1;33m-If you say 'yes', the current one will be deleted and a new one with the same title will be created; \033[0m")
                    print("\033[1;33m-If you say 'no', the current one will be opened and loaded into memory \033[0m")
                    while True:
                        ans = input()
                        if ans == 'y' or ans == 'yes':
                            print("\033[0;31m [Note] The existing KB has been deleted \033[0m")
                            shutil.rmtree(filep)
                            break
                        elif ans == 'n' or ans == 'no':
                            self.load_KB(os.path.join(filep, title + '.nxkb'))
                            create_flag = False
                            break
                        else:
                            print('\033[1;31m [Warning] Invalid order! \033[0m')

                if create_flag:
                    # Create a new KB
                    self.g = nx.DiGraph(title=title, node_number_dict={'tool': []})
                    filename = os.path.join(self.KBpath, title)
                    os.mkdir(filename)
                    filename = os.path.join(self.KBpath, title, 'Objects')
                    os.mkdir(filename)
                    filename = os.path.join(self.KBpath, title, 'Motions')
                    os.mkdir(filename)
                    filename = os.path.join(self.KBpath, title, title + '.nxkb')
                    self.save_KB(filename)
                    print("\033[1;34m [Note] Knowledge base created successfully...\033[0m")

            # Open an existing knowledge base
            match = re.match('open', order)
            if match is not None:
                title = order[5:]
                self.title = title
                filep = os.path.join(self.KBpath, title, title + '.nxkb')
                try:
                    self.load_KB(filep)
                except FileNotFoundError:
                    print("[Note] Knowledge base file", filep, "not found. Please choose your KB again...")

            if self.g is not None:
                print("\033[1;34;0m [Note] Knowledge base opened successfully...\n \033[0m")
                print('\033[1;34;0m <-------------------------- ' + title + ' --------------------------> \033[0m')
                self.IR = Vision.ImageRecognizer(self.KBpath, title)

                return
            else:
                print('\033[0;31m [Warning] Invalid order, Please say it again ... \033[0m')

    def interactiveSession(self):
        """Interacting with ontology knowledge base.

            Users can instruct knowledge base to:
            1) Recognize and then learn objects in the given scenario;
            2) Record and then recognize actions;
            3) Organize object vertices and action vertices as a directed graph according to 
            the logical and temporal relation entailed in instructional speech;
            4) Load or store a graph as binary file(*.nxkb).
           """
        try:
            self.x = threading.Thread(target=self.testThreading, args=())
            self.x.start()

            while self.close_flag == False:
                self.handPosition = self.hd.detectHand()

                # Start to record action
                if self.record_start_flag:
                    print('[Note] Start recording action...\n [Note] The video path is ' + self.video_name)
                    self.actionVideo = cv2.VideoWriter(
                        filename=self.video_name,
                        fourcc=cv2.VideoWriter_fourcc(*'XVID'),
                        fps=25,
                        frameSize=(640, 480),
                        isColor=1)
                    self.record_start_flag = False
                    self.record_flag = True

                # Stop recording action
                if self.record_stop_flag:
                    print('[Note] Saving action video, please wait... ')
                    self.actionVideo.release()
                    self.record_flag = False
                    self.record_stop_flag = False

                if self.record_flag:
                    self.actionVideo.write(self.hd.img.plainImg)

                self.hd.out.write(self.hd.img.src)

                if self.draw_graph_flag:
                    self.draw_graph_flag = False
                    self.draw_graph()

                if cv2.waitKey(10) == 'q':
                    break

            self.hd.out.release()
            self.hd.img.cap.release()
            cv2.destroyAllWindows()
            plt.close('all')
            exit()

        except Exception as e:
            print('\033[0;31m [Error] An error has occurred. Save KB and quit... \033[0m')
            print(traceback.format_exc())

            self.save_KB(os.path.join(self.KBpath, self.title, self.title + '.nxkb'))
            self.IR.save_feature_file()
            cv2.destroyAllWindows()
            exit()

        return

    def add_process(self, objects, tools, motion, results):
        self.g.add_node(motion.name, node_prop=motion, node_type='Motion')
        for obj_node in objects:
            self.g.add_edge(obj_node.name, motion.name)
        for tool_node in tools:
            self.g.add_edge(tool_node.name, motion.name)
        for result_node in results:
            self.g.add_edge(motion.name, result_node.name)


    def draw_graph(self):
        labels = dict((node[0], '[' + node[1].get('node_prop').state[0] + ']') for node in self.g.nodes(data=True) if
                      isinstance(node[0], str))

        plt.figure()

        values = [self.val_map.get(node[1]['node_type'], 0.6) for node in self.g.nodes(data=True) if
                  isinstance(node[0], str)]
        pos = nx.circular_layout(self.g)
        nx.draw_networkx(self.g, pos, edge=self.g.edges(), label=labels, cmap=plt.get_cmap('jet'), node_color=values)

        plt.show()

    def update_object_node(self, node):
        name=node.name
        state=node.state
        contents=node.contents
        category=node.category
        img_path=node.img_path[0]

        graph_keys = self.g.graph['node_number_dict'].keys()

        if name in graph_keys:
            # Search previous nodes to see if this node has been added onto the graph before
            objnode_list = self.g.graph['node_number_dict'][name]
            search_idx = len(objnode_list) - 1

            while search_idx >= 0:
                if objnode_list[search_idx].category == category \
                        and objnode_list[search_idx].state == state \
                        and objnode_list[search_idx].contents == contents:
                    break
                search_idx -= 1

            # if this node is not a one that has been obtained before,
            # add this node onto the graph and update the node dictionary of the graph
            if search_idx < 0:
                temp_No = len(self.g.graph['node_number_dict'][name])
                newname = name + str(temp_No)
                img_path = os.path.join(img_path, newname + '_0.jpg')
                vertex = Vertex(name=newname, state=state, contents=contents, category=category,
                                imgpath=[img_path])
                self.g.add_node(newname, node_prop=vertex, node_type=category)
                self.g.graph['node_number_dict'][name].append(vertex)
                print('[Note] There are objects of the same class, so its name is changed to', newname)
                return vertex, img_path
            # otherwise this node will be replaced with the identical node which has been obtained before
            else:
                img_path = os.path.join(img_path, objnode_list[search_idx].name + '_' + str(len(objnode_list[search_idx].img_path)) + '.jpg')
                objnode_list[search_idx].img_path.append(img_path)
                print('[Note] Object node ', '"' + name + '"',
                      "is already in the Graph, so it will be changed to the previous one")
                return objnode_list[search_idx], img_path
        else:
            # if the class of this object is not on the node dictionary,
            # then create a new class and add this object onto the graph
            img_path = os.path.join(img_path, name + '0_0.jpg')
            vertex = Vertex(name=name + '0', state=state, contents=contents, category=category, imgpath=[img_path])
            print(vertex)
            self.g.add_node(name + '0', node_prop=vertex, node_type=category)
            self.g.graph['node_number_dict'].update({name: [vertex]})
            return vertex, img_path

    def testThreading(self):

        process_finish = 0
        # Three lists used to store the nodes in a process
        process_objectlist = []
        process_toollist = []
        process_resultlist = []

        # a list used to store those nodes which are not in process_objectlist
        previous_resultlist = []

        while True:

            # if the program is recording videos,
            if self.record_stop_flag:
                continue

            # When a process unit has been learned, the three lists will be cleared
            if process_finish == 1:
                process_objectlist.clear()
                process_toollist.clear()
                process_resultlist.clear()
                process_finish = 0

            print("""\033[1;33;0m Describe a process: 
Object  - say 'this object is apple.' to create a object vertex in the graph 
Tool    - say 'this tool is knife.' to create a tool vertex in the graph 
Motion  - say 'we use a knife to cut the apple, and get apple_slices.' to record the action to be implemented
Other expamples:
# ex1: we use a knife to cut the apple, and get apple_slices.  [tool][motion][obj], and get [result]
# ex2: we pick the apple_slices, and put them into a bowl.  [motion1][obj], and [motion] [tool]
# ex3: we pick the apple.   [motion][obj]
# ex4: we put down the apple.
# ex5: we squeeze salad_sauce onto apple_slices  [motion][obj] prep [obj]
\033[0m""")

            if self.mode == 'N':
                order = (input('Waiting for order...')).lower()
            else:
                order = (input_voice_secure(self.ARGS, self.model, 'Waiting for order...')).lower()
            # Learn a new vertex of knowledge
            match = re.match('this object is', order)
            if match is not None:
                # Describe this object
                state = ['']
                contents = ['']
                category = ''
                name = order[15:-1]

                while True:
                    # requiring...
                    if self.mode == 'N':
                        description = input('\033[1;33;0m Please decribe it (say "ok" to finish it)... \033[0m').lower()
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

                    # """ Say 'category' to specify its category """
                    prop = re.match('category', description)
                    if prop is not None:
                        category = description[9:]
                        print("[Note] ok! its category has been updated: " + category + '\n')
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
                            # Enquiring...
                            if self.mode == 'N':
                                s = input(
                                    '\033[1;33;0m Please describe its state (say "done" to finish it)... \033[0m').lower()
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

                    print('\033[0;31m [Warning] Invalid order, Please say it again ... \033[0m')

                """
                UPDATE the No. of the OBJECT node
                """
                img_path = os.path.join(self.KBpath, self.title, 'Objects')
                vertex = Vertex(name=name, state=state, contents=contents, category=category,
                                imgpath=[img_path])
                vertex, img_path = self.update_object_node(vertex)
                process_objectlist.append(vertex)

                # Take a photo
                object_pos = self.handPosition[0]
                print('[Note] The program will take a photo in 2 seconds, please move away your hands...')
                cv2.waitKey(2000)  # Please move your hands away from the object

                object_img = self.hd.img.plainImg[object_pos[1]:object_pos[1] + object_pos[3], \
                             object_pos[0]:object_pos[0] + object_pos[2], :]

                cv2.destroyAllWindows()
                cv2.imshow(name, object_img)
                cv2.waitKey(1)
                cv2.imwrite(img_path, object_img)
                print('[Note] Image path:', img_path)
                print('[Note] Extract features from the image. Please wait...')
                fts = self.IR.extract_features(object_img)
                self.IR.append_feature(fts, img_path)
                print('[Note] Features extracted and saved successfully!.\n')

                continue

            # Learning tool objects
            match = re.match('this tool is', order)
            if match is not None:
                tool_name = order[13:-1]
                img_path = os.path.join(self.title, 'Objects')

                toolnode_list=self.g.graph['node_number_dict']['tool']
                create_flag=False

                if len(toolnode_list)==0:
                    create_flag=True
                else:
                    idx=len(toolnode_list)-1
                    while idx>=0:
                        if toolnode_list[idx].name == tool_name:
                            break
                        idx-=1
                    if idx<0:
                        create_flag=True
                    else:
                        num=str(len(toolnode_list[idx].img_path))
                        img_path = os.path.join(img_path, tool_name + '_'+num+'.jpg')
                        toolnode_list[idx].img_path.append(img_path)
                        process_toollist.append(toolnode_list[idx])
                        print('[Note] This tool is already in the knowledge graph')
                        print(toolnode_list[idx])

                if create_flag:
                    img_path = os.path.join(img_path, tool_name + '_0.jpg')
                    tool = Vertex(name=tool_name, category='Tool', state=['clean'], imgpath=[img_path])
                    self.g.add_node(tool_name, node_prop=tool, node_type=tool.category)
                    self.g.graph['node_number_dict']['tool'].append(tool)
                    process_toollist.append(tool)
                    print(tool)


                # Take a photo
                tool_pos = self.handPosition[0]
                print('[Note] The program will take a photo in 2 seconds, please move away your hands...')
                cv2.waitKey(2000)  # Please move your hands away from the object
                tool_img = self.hd.img.plainImg[tool_pos[1]:tool_pos[1] + tool_pos[3], \
                           tool_pos[0]:tool_pos[0] + tool_pos[2], :]

                cv2.destroyAllWindows()
                cv2.imshow(tool_name, tool_img)
                cv2.waitKey(1)
                print('[Note] Image path:',img_path)
                cv2.imwrite(img_path, tool_img)

                print('[Note] Extract features from the image. Please wait...\n')
                fts = self.IR.extract_features(tool_img)
                self.IR.append_feature(fts, img_path)

                continue

            match = re.match('save', order)
            if match is not None:

                self.save_KB(os.path.join(self.KBpath, self.title, self.title + '.nxkb'))
                self.IR.save_feature_file()
                print('[Note] The knowledge graph and all features have been saved!\n')
                continue

            match = re.match('display', order)
            if match is not None:
                self.draw_graph_flag = True
                continue

            match = re.match('quit', order)
            if match is not None:
                self.save_KB(os.path.join(self.KBpath, self.title, self.title + '.nxkb'))
                self.IR.save_feature_file()
                self.close_flag = True
                print('[Note] save and quit')

                break

            match = re.match('we', order)
            # ex1: we use a knife to cut the apple, and get apple_slices  [tool][motion][obj], and get [result]
            # ex2: we pick the apple_slices, and put them into a bowl.  [motion1][obj], and [motion] [tool]
            # ex3: we pick the apple   [motion][obj]
            # ex4: we put down the apple
            # ex5: we squeeze salad_sauce onto apple_slices  [motion][obj] prep [obj]

            if match is not None:
                previous_resultlist.clear()
                process_finish = 1
                if 'use' in order:

                    """
                    Extract the name of the object being operated
                    """
                    comma_idx = len(order) - 1
                    while comma_idx >= 0:
                        if order[comma_idx] == ',':
                            break
                        comma_idx -= 1

                    space_before_obj_idx = comma_idx
                    while space_before_obj_idx >= 0:
                        if order[space_before_obj_idx] == ' ':
                            break
                        space_before_obj_idx -= 1

                    obj_name = order[space_before_obj_idx + 1:comma_idx]

                    """
                    Search for previously learned node to see if the object being operated has been learned;
                    if the object being operated has been learned, then the process will be added onto the graph;
                    otherwise, the process will be failed, due to lack of information of the object being operated.
                    """
                    # Search mechanism step 1: search in process_objectlist
                    idx = 0
                    while idx < len(process_objectlist):
                        if obj_name == process_objectlist[idx].name:
                            break
                        idx += 1

                    # Search mechanism step 2: search in the node dictionary
                    if idx == len(process_objectlist):
                        if obj_name in self.g.graph['node_number_dict'].keys():
                            previous_objnode=self.g.graph['node_number_dict'][obj_name][-1]
                            process_objectlist.append(previous_objnode)
                            print('[Note] The object being operated "{}" was obtained long ago'.format(previous_objnode.name))
                        else:
                            print('\033[0;31m[Warning] The result node "{}" cannot be found in the graph. Please describe it first.\n \033[0m'.format(obj_name))
                            continue

                    """
                    Extract the name of the tool mentioned in the order
                    """
                    to_idx = 7
                    while to_idx < len(order):
                        if order[to_idx] == 't' \
                                and order[to_idx + 1] == 'o' \
                                and order[to_idx + 2] == ' ':
                            break
                        to_idx += 1

                    space_before_tool_idx = to_idx - 2
                    while space_before_tool_idx >= 0:
                        if order[space_before_tool_idx] == ' ':
                            break
                        space_before_tool_idx -= 1
                    tool_name = order[space_before_tool_idx + 1:to_idx - 1]

                    # Search process_toollist to find out the position of the tool node
                    # Firstly, search in process_toollist
                    find_flag = False
                    for tool_node in process_toollist:
                        if tool_node.name == tool_name:
                            find_flag = True
                            break

                    # If the tool node is not in process_toollist, which means this node may have been obtained before,
                    # continue to search in prev_obj_nodelist
                    if not find_flag:
                        toolnode_list = self.g.graph['node_number_dict'].get('tool')
                        # If the key'tool' is not in the node dictionary,
                        tool_idx = len(toolnode_list) - 1
                        while tool_idx >= 0:
                            if toolnode_list[tool_idx].name == tool_name:
                                find_flag = True
                                process_toollist = [toolnode_list[tool_idx]]
                                break
                            tool_idx -= 1

                    if not find_flag:
                        print('\033[0;31m[Warning]The tool node "' + tool_name + '" cannot be found! Please describe it first.\n \033[0m')
                        continue

                    """
                    Extrcat the information of the MOTION
                    """
                    space_after_motion_idx = to_idx + 4

                    while space_after_motion_idx < len(order):
                        if order[space_after_motion_idx] == ' ':
                            break
                        space_after_motion_idx += 1

                    action_name = order[to_idx + 3:space_after_motion_idx]
                    self.video_name = os.path.join(self.KBpath, self.title, 'Motions', action_name + '.avi')
                    self.record_start_flag = True

                    # Start recording a video. Stop when 'finish' is confirmed
                    while True:
                        command = (input("\033[1;33;0m [Note] Say 'finish' to end recording your action...\n \033[0m")).lower()
                        # Speech Recognition
                        match = re.match('finish', command)
                        if match is not None:
                            self.record_stop_flag = True
                            break

                    """
                    Create a MOTION node
                    """
                    process_motion = Vertex(name=action_name, state=None, contents=None, category='Motion',
                                            imgpath=[self.video_name])
                    """
                    Update the No. of the motion node in the node dictionary of the graph
                    """
                    graph_keys = self.g.graph['node_number_dict'].keys()

                    if action_name in graph_keys:
                        # The No. of the latest matched node
                        temp_No = len(self.g.graph['node_number_dict'][action_name])
                        process_motion.name += str(temp_No)
                        self.g.graph['node_number_dict'][action_name].append(process_motion)
                    else:
                        process_motion.name += '0'
                        self.g.graph['node_number_dict'].update({action_name: [process_motion]})


                    """
                    Extract properties from the result of the operation
                    """
                    space_before_result_idx = len(order) - 1
                    while space_before_result_idx >= 0:
                        if order[space_before_result_idx] == ' ':
                            break
                        space_before_result_idx -= 1

                    name=order[space_before_result_idx + 1:-1]
                    img_path = os.path.join(self.KBpath, self.title, 'Objects')
                    result = Vertex(name=name, state=['be_' + process_motion.name], imgpath=[img_path])
                    """
                    Update the No. of every RESULT node
                    """
                    updated_result, img_path = self.update_object_node(result)
                    process_resultlist.append(updated_result)

                    # Take a photo
                    object_pos = self.handPosition[0]
                    print('[Note] The program will take a photo in 2 seconds, please move away your hands...')
                    cv2.waitKey(2000)  # Please move your hands away from the object

                    object_img = self.hd.img.plainImg[object_pos[1]:object_pos[1] + object_pos[3], \
                                 object_pos[0]:object_pos[0] + object_pos[2], :]

                    cv2.destroyAllWindows()
                    cv2.imshow(name, object_img)
                    cv2.waitKey(1)
                    cv2.imwrite(img_path, object_img)
                    print('[Note] Image path:', img_path)
                    print('[Note] Extract features from the image. Please wait...')
                    fts = self.IR.extract_features(object_img)
                    self.IR.append_feature(fts, img_path)
                    print('[Note] Features extracted and saved successfully!.\n')
 
                    # Add nodes onto the graph
                    self.add_process(process_objectlist,
                                     process_toollist,
                                     process_motion,
                                     process_resultlist)

                    print("\033[1;33;0m Please check the results below..\n \033[0m")
                    # for i in previous_resultlist:
                    #     print(i)
                    for i in process_objectlist:
                        print(i)
                    for i in process_toollist:
                        print(i)
                    print(process_motion)
                    for i in process_resultlist:
                        print(i)

                    self.draw_graph_flag=True
                    continue
                else:
                    if 'and' in order:
                        pass

            match = re.match('what', order)
            if match is not None:
                obj_pos = self.handPosition[0]
                print('[Note] The program will take a photo in 2 seconds, please move away your hands...\n')
                cv2.waitKey(2000)  # Please move your hands away from the object
                obj_img = self.hd.img.plainImg[obj_pos[1]:obj_pos[1] + obj_pos[3], \
                          obj_pos[0]:obj_pos[0] + obj_pos[2], :]

                cv2.imshow("object image", obj_img)
                cv2.waitKey(1)

                print('[Note] Searching similar images in database. Please wait...')
                nearest_img_paths, _ = self.IR.match(obj_img, 1)
                print('\033[1;34;0m[Note] Found matched image: \033[0m', end='')
                print(nearest_img_paths[0])
                matched_img = cv2.imread(nearest_img_paths[0])

                slashidx = -1
                while nearest_img_paths[0][slashidx] != '\\':
                    slashidx -= 1
                obj_name = nearest_img_paths[0][slashidx + 1:-3]

                print('\033[1;34;0m This object is \033[0m' + obj_name)
                cv2.imshow("match image", matched_img)
                cv2.waitKey(0)
                cv2.destroyWindow("match image")
                print()
                continue

            print('\033[0;31m Invalid order...\n \033[0m')

    def save_KB(self, filename):
        """ Save a knowledge base to a local file """
        with open(filename, 'wb') as f:
            pickle.dump(self.g, f)  # 存入知识图谱到本地存储

    def load_KB(self, filename):
        """ Load a knowledge base from a local file """
        with open(filename, 'rb') as f:
            self.g = pickle.load(f)


testG = KnowledgeGraph(args.kbpath)
testG.initSession()
testG.interactiveSession()



