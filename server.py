import argparse
from flask import Flask, jsonify, request
from network import Network
import os
import sys
app = Flask(__name__)

print(__name__)
@app.route("/detect")
def detect():
    if request.method == 'GET':
        input_path = request.args['input']
        
        global net
        
        if os.path.isdir(input_path):
            result = net.detect_folder(input_path)
            
        elif os.path.isfile(input_path):
            result = net.detect(input_path)
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
        
def parse_args():
    
    NETS = ["full", "lite"]
    
    parser = argparse.ArgumentParser(description='Flask server containing PVANET in Caffe')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--net', dest='net', help='Version of PVANET to use',
                        choices=NETS, default='full')
    args = parser.parse_args()

    return args   


if __name__ == '__main__':
    
    args = parse_args()
    
    net= Network(args.net)
    app.run(host='0.0.0.0')
    
