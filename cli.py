import click
from subprocess import Popen, STDOUT
import requests
import os
import shelve
from time import sleep

@click.group()
def main():
    pass

@click.command("start",help="Start the Flask server and load the model on GPU")
@click.option('--net', default="full")
def start(net):
    
    #Check if the server is alreay running
    server_status = shelve.open("server_status")
    
    if "status" in server_status:
        print("The server is already with pid: {}".format(server_status["status"]))
              
    else:
        cmd = ["python", "server.py"]
        FNULL = open(os.devnull, 'w')
        server_process = Popen(cmd, stdout=FNULL, stderr=STDOUT)
    
        #Store server status the in persistent way
        server_status["status"] = server_process.pid
        server_status.sync()
        server_status.close()
        print("The Flask server starts with pid {}".format(server_process.pid))
        sleep(2)
        print("PVANET-{} has loaded on GPU".format(net))
   
    return
              
             
@click.command(help="Stop the flask server and unload the model from GPU")
def stop():
    
    server_status = shelve.open("server_status")
    if "status" in server_status:
        keyword = "Oh Yeah Baby!"
        data = {'keyword': keyword}
        address = 'http://localhost:5000/shutdown'
        r = requests.post(address, params=data)
        print("Object Detection server with pid {} stopped".format(server_status["status"]))
        print("Memory released from GPU")
              
        #Store server status the in persistent way
       
        server_status.clear()
        server_status.sync()
        server_status.close()
              
    else:
        print("The server was not running")
       
    
    
    return

@click.command(help="Detect the given folder or input image and returns JSON output in stdout.")
@click.argument("input_location")
def run(input_location):
    data = {'input': input_location}
    address = 'http://localhost:5000/detect'
    try:
        r = requests.get(address, params=data)
        click.echo(r.text)
    except requests.exceptions.ConnectionError:
        print("The server is down. Please run 'obd start' to start the server")
    return


main.add_command(start)
main.add_command(stop)
main.add_command(run)