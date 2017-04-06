from __future__ import print_function
import argparse
from flask import Flask, jsonify, request
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from network import Network

app = Flask(__name__)
#logging.basicConfig(filename='logs/server.log',level=logging.DEBUG)
flask_logger = logging.getLogger()





@app.route("/detect")
def detect():
    
    if request.method == 'GET':
        input_path = os.path.join(os.getcwd(), request.args['input'])
        
        global net
        
        if os.path.isdir(input_path):
            result = net.detect_folder(input_path)
            
        elif os.path.isfile(input_path):
            result = net.detect(input_path)
        else:
            result = {"error": "The path {} does not exist".format(input_path)}
        return jsonify(result)     

    
@app.route("/shutdown", methods=['POST'])
def shutdown():
    keyword = "Oh Yeah Baby!"
    if keyword == request.args['keyword']:
        print("Flask server is going down.")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return "Server Down"
    else:
        print("The keyword is incorrect!")
        
@app.route("/info")
def get_info():
    return jsonify(net.info) 
        
def parse_args():
    
    NETS = ["full", "lite"]
    
    parser = argparse.ArgumentParser(description='Flask server containing PVANET in Caffe')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--net', dest='net', help='Version of PVANET to use',
                        choices=NETS, default='full')
    parser.add_argument('--debug', dest='debug', help='Display all the message to console instead of logging',
                        action='store_true')
    args = parser.parse_args()

    return args   

    flask_logger.addHandler(handler)
    
class LoggerWriter:
    def __init__(self, level):
        # self.level is really like using log.debug(message)
        # at least in my case
        self.level = level

    def write(self, message):
        # if statement reduces the amount of newlines that are
        # printed to the logger
        if message != '\n':
            self.level(message)

    def flush(self):
        # create a flush method so things can be flushed when
        # the system wants to. Not sure if simply 'printing'
        # sys.stderr is the correct way to do it, but it seemed
        # to work properly for me.
        self.level(sys.stderr)   
    
 

if __name__ == '__main__':
    
    LOG_DIR = "/root/Object-Detection/logs"
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)

    handler = RotatingFileHandler('{}/server.log'.format(LOG_DIR), maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    flask_logger = logging.getLogger()
    
    flask_logger.addHandler(handler)
   
    
    args = parse_args()
    
    
    
    net= Network(args.net)
   
    #flask_logger.info('Attempt to turn on the server')
    
    if not args.debug:
        sys.stdout = LoggerWriter(flask_logger.info)
        sys.stderr = LoggerWriter(flask_logger.warn)
        flask_logger.setLevel(logging.DEBUG)

   

    app.run(host='0.0.0.0', debug=args.debug)  
    