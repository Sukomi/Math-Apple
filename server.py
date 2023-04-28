import json
from flask import Flask
from flask_cors import CORS
from flask import request

from PIL import Image
import numpy as np

import multiprocessing
from time import time
import os
import sys
import getopt
import traceback


app = Flask(__name__)
CORS(app)

FRAME_DIR = "frames"
FILE_SUF = "png"
BLOCK_SIZE = 25
ASCII_CHARS = ["@","#","S","%","?","*","+",";",":",",","."]
NEW_WIDTH = 100

frame = multiprocessing.Value('i',0)
frame_latex = 0

def help():
    print('Works like a regular calculator.\n Use the input \"bad apple\" to start the fun!')

def resize_image(data, new_width=100):
    width, height = data.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_image = data.resize((new_width, new_height))
    return resized_image

def grayify(data):
    grayscale_image = data.convert("L")
    return grayscale_image

def img_to_ascii(data):
   image = Image.open((FRAME_DIR + '/frame%d.%s' % (data+1, FILE_SUF)))
   new_image = grayify(resize_image(image, NEW_WIDTH))
   pixels = new_image.getdata()
   characters =  "".join([ASCII_CHARS[pixel//25] for pixel in pixels])
   with frame.get_lock():
       frame.value += 1
   print('\r--> Frame %d/%d' % (frame.value, len(os.listdir(FRAME_DIR))), end='')
   return(characters)

   
@app.route('/')
def index():
    frame = int(request.args.get('frame'))
    if frame >= len(os.listdir(FRAME_DIR)):
        return {'result': None}
    
    block = []
    number_of_frames = min(frame + BLOCK_SIZE, len(os.listdir(FRAME_DIR))) - frame
    for i in range(frame, frame + number_of_frames):
        pixel_count = len(frame_latex[i])
        block.append("\n".join(frame_latex[i][j:(j+NEW_WIDTH)] for j in range(0, pixel_count, NEW_WIDTH)))
    return json.dumps({'result': block, 'number_of_frames': number_of_frames})

@app.route('/init')
def init():
    return json.dumps({'total_frames': len(os.listdir(FRAME_DIR)),})

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:e:c:bdlg", ['static', 'block=', 'maxpblock=','yes'])

    except getopt.GetoptError:
        print('Error: Invalid argument(s)\n')
        help()
        sys.exit(2)

    eula = ''

    try:
        for opt, arg in opts:
            if opt == '-h':
                help()
                sys.exit()
            elif opt == '-f':
                FRAME_DIR = arg
            elif opt == '-e':
                FILE_SUF = arg
            elif opt == '--block':
                BLOCK_SIZE = int(arg)
            elif opt == '--yes':
                eula = 'y'
        frame_latex = range(len(os.listdir(FRAME_DIR)))
    
    except TypeError:
        print('Error: Invalid argument(s)\n')
        help()
        sys.exit(2)

    with multiprocessing.Pool(processes = multiprocessing.cpu_count()) as pool:
        print("BAD APPLE TIME!")
        print("Arvain 2023")
        print("https://github.com/Sukomi/Math-Apple")
        print("Are you ready?")
        while eula != 'y':
            eula = input('                                      Agree (y/n)? ')
            if eula == 'n':
                quit()
        print('-----------------------------')
        print('Processing %d frames... Please wait for processing to finish\n' % len(os.listdir(FRAME_DIR)))
        start = time()

        frame_latex = pool.map(img_to_ascii, frame_latex)

        print('\r--> Processing complete in %.1f seconds\n' % (time() - start))
        

        app.run()


