from flask import Flask, send_from_directory
import subprocess

app = Flask(__name__)

@app.route('/run/<app_type>')
def run_app(app_type):
    if app_type == 'admin':
        subprocess.Popen(['python', 'adminbutton.py'])
        return "Admin application started!"
    elif app_type == 'new_user':
        subprocess.Popen(['python', 'VISIO-LOCK.py'])
        return "New User application started!"
    else:
        return "Unknown application type!"

if __name__ == '__main__':
    app.run(port=5000)
