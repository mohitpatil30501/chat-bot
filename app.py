import time
import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
socket = SocketIO(app)


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route('/chat', methods=['POST'])
def chat():
    username = str(request.form.get('username'))
    room = username + str(int(time.time()))
    if username and room:
        return render_template("chat.html", username=username, room=room)
    else:
        return redirect(url_for('home'))


@socket.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'], data['room'], data['message']))
    socket.emit('receive_message', data, room=data['room'])

    response = requests.post('http://chat-bot-mohit.herokuapp.com:5005/webhooks/rest/webhook',
                             json={'message': data['message']})
    for i in response.json():
        if 'text' in i.keys():
            bot_message = i['text']
        elif 'image' in i.keys():
            bot_message = i['image']
        else:
            bot_message = ""
        print("Bot:", bot_message)
        bot_data = {
            'username': 'Bot',
            'room': data['room'],
            'message': bot_message
        }
        app.logger.info("{} has sent message to the room {}: {}".format(bot_data['username'], bot_data['room'],
                                                                        bot_data['message']))
        socket.emit('receive_message', bot_data, room=bot_data['room'])


@socket.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socket.emit('join_room_announcement', data, room=data['room'])


if __name__ == '__main__':
    socket.run(app, debug=False, host='chat-bot-mohit.herokuapp.com', port=5000)
