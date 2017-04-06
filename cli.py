import click
from subprocess import Popen, STDOUT, PIPE, check_output,CalledProcessError
import requests
import os
from time import sleep
import json

def get_pid(port=5000):
    cmd = ["lsof", "-i", ":{}".format(port)]
    try:
        
        output = check_output(cmd)
    except CalledProcessError:
        return 0
    lines = output.split("\n")
    if lines:
        pid = lines[1].split()[1]
        return pid
    else:
        return 0

        

@click.group()
def main():
    pass
 


@click.command("start",help="Start the Flask server and load the model on GPU")
@click.option('--net', default="full")
@click.option('--debug/--no-debug', default=False)

def start(net, debug):
    
    #Check if the server is alreay running
    pid = get_pid()
    if pid:
        print("The server is already runngin with pid: {}".format(pid))
              
    else:
           
        
        
        cmd = ["python", "/root/Object-Detection/server.py"]      
        if debug:
            cmd += ["--debug"]
        server_process = Popen(cmd)
       

      

        print("The Flask server starts with pid {}".format(server_process.pid))
        sleep(2)
        print("PVANET-{} has loaded on GPU".format(net))
    return
              


  
@click.command(help="Stop the flask server and unload the model from GPU")
def stop():
    pid = get_pid()
   
    if pid:
        keyword = "Oh Yeah Baby!"
        data = {'keyword': keyword}
        address = 'http://localhost:5000/shutdown'
        r = requests.post(address, params=data)
        print("Object Detection server with pid {} stopped".format(pid))
        print("Memory released from GPU")           
                     
    else:
        print("The server was not running")
       
   
    
    return

@click.command(help="Detect the given folder or input image and returns JSON output in stdout.")
@click.argument("input_location")
def run(input_location):
    input_location = os.path.join(os.getcwd(), input_location)
    if os.path.exists(input_location):
        data = {'input': input_location}
        address = 'http://localhost:5000/detect'
        try:
            r = requests.get(address, params=data)
            click.echo(r.text)
        except requests.exceptions.ConnectionError:
            click.echo("The server is down. Please run 'obd start' to start the server")
    else:
        click.echo("The path: {} does not exist".format(input_location))
        #click.echo(json.dumps(error_message))
    return

    if keyword == request.args['keyword']:
        print("Flask server is going down.")
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return "Server Down"
    else:
        print("The keyword is incorrect!")
@click.command(help="Status of the Flask server.")
def status():
    pid = get_pid()
    if pid:
        print("The server is running with pid: {}".format(pid))
        
        address = 'http://localhost:5000/info'

        r = requests.get(address)
        click.echo(r.text)
       
    else:
        print("The server is not running.")
    
print(os.getcwd())

main.add_command(start)
main.add_command(stop)
main.add_command(run)
main.add_command(status)