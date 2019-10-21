# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 15:59:14 2019
Last modified on Oct. 7 10:07 2019
@author: 
"""
"""
Ontology based adjacency graph 

"""
import Brain as KB # KB framework

import Vision # Image recognition

import argparse

import re

import os

parser = argparse.ArgumentParser()
parser.add_argument("--kbpath",
                    help="The path where a previous KB was stored.")
# parser.add_argument("--imgpath",
#                     help="The path where images were stored.")
args = parser.parse_args()

cur_gpath=args.kbpath # The file where all KBs are stored

# Activate session
while(1):
    option = input('Wake up...')
    start=re.search('activate',option.lower())
    if start is not None:
        try:
            capture = cv2.VideoCapture(1)
        except:
            print('Webcam open failure!')
        break;




while(1):
    order = (input('Waiting for orders...')).lower()
    # New knowledge base
    match = re.match('new', order)
    if match is not None:
        title=order[4:]
        if len(title)==0:  # If title was not specified, it will be specified as current local time
            title=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        g=KB.Graph(title=title,directed=True)
        filename = cur_gpath+'\\'+title
        os.mkdir(filename)
        filename = cur_gpath + '\\'+ title + '\\Objects'
        os.mkdir(filename)
        filename = cur_gpath + '\\' + title + '\\Motions'
        os.mkdir(filename)
        filename = cur_gpath + '\\' + title + '.kb'
        KB.save_KB(g,filename)

        continue

    # Learn a new vertex of knowledge
    match = re.match('this object is',order)
    if match is not None:
        # Describe this object
        state=None
        contents=None
        category=None
        name = order[15:]

        while(1):
            descri = input('Please decribe it...')

            prop = re.match('ok',descri)
            if prop is not None:
                break

            prop = re.match('category', descri)
            if prop is not None:
                category = descri[9:]
                continue

            prop = re.match('contents', descri)
            if prop is not None:
                contents=descri.split()
                contents=contents[1:]
                continue

            prop = re.match('state', descri)
            if prop is not None:
                state=descri[6:]
                continue


        vertex=KB.Vertex(name=name, state=[state], contents=contents, category=category)
        temp=g.find_duplicate(vertex)
        if temp is not

        g.insert_vertex(vertex)
        print('I have learned this object。。。')

        # Take photo
        ret, frame = capture.read()
        img_path=cur_gpath+'\\'+'Objects'+
        cv2.imwrite(img_path, frame)
        cv2.imshow('img', frame)
        cv2.waitKey()
        cv2.destroyAllWindows()






save_file = 'E:\\Research\\graph.txt'
save_KB(g3, save_file)
g4 = load_KB(save_file)

g4.display_processes()
print(g4)

G = Graph("Apple")
count = 0
while (1):
    option = input("请输入所要执行的操作的编号\n0:建立新知识图谱 1:输入图像信息 2:输入视频信息 3:输入语音信息")

    if option == '1':
        capture = cv2.VideoCapture(1)
        ret, frame = capture.read()
        img_path = 'E:\\Research\\' + str(count) + '.jpg'
        cv2.imwrite(img_path, frame)
        cv2.imshow('img', frame)
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = resnet50.preprocess_input(x)

        preds = model.predict(x)
        result = resnet50.decode_predictions(preds, top=1)[0][0][1]

        v = Vertex(1, result, ['Unchopped'], None, 'Fruit', img_path)
        print(v)
        G.insert_vertex(v)
