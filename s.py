import socket
from _thread import *
import sys
import json


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = '192.168.56.1'
port = 5555

server_ip = socket.gethostbyname(server)


########## GAME CONFIGURATION
DY_SPEED = 1
DX_SPEED = 1
WINNING_SCORE = 3
class obj:
    pass
# Score


scoreA = 0
scoreB = 0
width = 800
height = 600

# PADDLE A

a = obj()
a.x = 0.0625 * width - width / 2
a.y = 0
a.gotPoint = 0

# PADDLE B
b  = obj()
b.x = width / 2 - 0.0625 * width
b.y = 0
b.gotPoint = 0

# BALL
ball = obj()
ball.dx = DX_SPEED
ball.dy = DY_SPEED
ball.x = 0
ball.y = 0
ball.isMoving = True


##############################
def reset():
    global a, b, width, height, ball,scoreA,scoreB
    # PADDLE A


    a.x = 0.0625 * width - width / 2
    a.y = 0
    a.gotPoint = 0

    # PADDLE B
    b.x = width / 2 - 0.0625 * width
    b.y = 0
    b.gotPoint = 0

    # BALL

    ball.dx = DX_SPEED
    ball.dy = DY_SPEED
    ball.x = 0
    ball.y = 0
    ball.isMoving = True
    scoreB = 0
    scoreA = 0

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))




prevData = {'ball.x': ball.x, 'ball.y': ball.y, 'a.x': a.x, 'a.y': a.y,
                            'a.gotPoint': a.gotPoint,'b.x': b.x, 'b.y': b.y,
                            'b.gotPoint': b.gotPoint, 'isBallMoving': 0, 'scoreA': scoreA, 'scoreB': scoreB, 'close': 0, 'winner': -1}

s.listen(2)
print("Waiting for a connection")

currentId = 0

sendData = ''
def threaded_client(conn):
    global currentId, a, b, ball, scoreA, scoreB, width, height, sendData, prevData
    conn.send(str.encode(str(currentId)))
    currentId += 1

    try:
        while True:
            data = conn.recv(2048).decode('utf-8')
            reply = json.loads(data)
            if len(reply) == 0:
                conn.send(str.encode("Goodbye"))
                break
            if reply['ctrl'] == 0:
                prevData = {'ball.x': ball.x, 'ball.y': ball.y, 'a.x': a.x, 'a.y': a.y, 'a.gotPoint': a.gotPoint,
                            'b.x': b.x, 'b.y': b.y, 'b.gotPoint': b.gotPoint, 'isBallMoving': 1, 'scoreA': scoreA,
                            'scoreB': scoreB, 'close': 1, 'winner': -1}
                sendData = json.dumps(prevData)
                conn.sendall(str.encode(sendData))
                conn.close()
                return
            elif reply['ctrl'] == 1:

                reset()

                prevData = {'ball.x': ball.x, 'ball.y': ball.y, 'a.x': a.x, 'a.y': a.y,'a.gotPoint': a.gotPoint, 'b.x': b.x, 'b.y': b.y,'b.gotPoint': b.gotPoint, 'isBallMoving': 1, 'scoreA': scoreA, 'scoreB': scoreB, 'close': 0, 'winner': -1}
                sendData = json.dumps(prevData)
                conn.sendall(str.encode(sendData))
                continue
            else:
            # print(reply)
            # Moving Ball
                if ball.isMoving:
                    # print('ball is moving')
                    ball.x = ball.x + ball.dx
                    ball.y = ball.y + ball.dy
                    # print('MOVING BALL : ' + str(ball.x) + '   ' + str(ball.y))
                elif a.gotPoint == 1:
                    # print('A got point move ball')
                    ball.x = b.x - 0.04 * width
                    ball.y = b.y + 0.01 * height
                    if reply['space'] == 1:
                        ball.dx *= -1
                        ball.isMoving = True
                        a.gotPoint = 0
                elif b.gotPoint == 1:
                    # print('B got point move ball')
                    ball.x = a.x + 0.04 * width
                    ball.y = a.y + 0.01 * height
                    if reply['space'] == 0:
                        ball.dx *= -1
                        ball.isMoving = True
                        b.gotPoint = 0



                lolh = 0.48333 * height
                if ball.y > lolh:
                    ball.y = lolh
                    ball.dy *= -1

                if ball.y < -lolh:
                    ball.y = -lolh
                    ball.dy *= -1

                # Player on left (A) got point
                lolw = 0.4875 * width
                if ball.x > lolw:
                    ball.isMoving = False

                    print('A GOT POINT = {} .  BALL ( X , Y ) = ( {} , {} )'.format(scoreA,str(b.x),str(b.y)))
                    ball.x = b.x - 0.012 * width
                    ball.y = b.y + 0.01 * height
                    a.gotPoint = 1

                    scoreA += 1


                # Player on right (B) got point
                if ball.x < -lolw:
                    print('B GOT POINT = {} . BALL ( X , Y ) = ( {} , {} )'.format(scoreB,str(b.x),str(b.y)))
                    ball.isMoving = False
                    ball.x = a.x + 0.02 * width
                    ball.y = a.y + 0.01 * height
                    b.gotPoint = 1

                    scoreB += 1

                # Collision
                lolcw = [0.425 * width, 0.4375 * width]
                #        340         350
                lolch = 0.091666 * height  # 55
                if (ball.x > lolcw[0] and ball.x < lolcw[1]) and (
                        ball.y < b.y + lolch and ball.y > b.y - lolch):

                    ball.x = lolcw[0]
                    ball.dx *= -1

                if (ball.x < -lolcw[0] and ball.x > -lolcw[1]) and (
                        ball.y < a.y + lolch and ball.y > a.y - lolch):
                    # ball.setx(-lolcw[0])
                    ball.x = -lolcw[0]
                    ball.dx *= -1
                # print('X : ' + str(ball.xcor()) + ' Y : ' + str(ball.ycor()))
                close = 1 if scoreA >= WINNING_SCORE or scoreB >= WINNING_SCORE else 0
                winner = -1 if close == 0 else 0 if scoreA >= WINNING_SCORE else 1

                prevData = {'ball.x': ball.x, 'ball.y': ball.y, 'a.x': a.x, 'a.y': a.y,
                            'a.gotPoint': a.gotPoint,
                            'b.x': b.x, 'b.y': b.y, 'b.gotPoint': b.gotPoint,
                            'isBallMoving': (1 if ball.isMoving else 0), 'scoreA': scoreA, 'scoreB': scoreB, 'close': close, 'winner': winner}

                if reply['a'] == 'none' and reply['b'] == 'none':
                    # prevData = {'ball.x': ball.x, 'ball.y': ball.y, 'a.x': a.x, 'a.y': a.y,
                    #             'a.gotPoint': a.gotPoint,'b.x': b.x, 'b.y': b.y,
                    #             'b.gotPoint': b.gotPoint, 'isBallMoving': (1 if ball.isMoving else 0), 'scoreA': scoreA, 'scoreB': scoreB, 'close': close}
                    # print('none none  ' + str(prevData) )
                    sendData = json.dumps(prevData)

                    conn.sendall(str.encode(sendData))
                else:
                    print("Recieved: " + str(reply))
                    if reply['space'] == 1:
                        if a.gotPoint == 1:
                            ball.dx = - ball.dx
                            a.gotPoint = 0
                        elif b.gotPoint == 1:
                            ball.dx = - ball.dx
                            b.gotPoint = 0
                    if reply['a'] == 'up':
                        a.y = a.y + 20
                    elif reply['a'] == 'down':
                        a.y = a.y - 20
                    elif reply['b'] == 'up':
                        b.y = b.y + 20
                    else:
                        b.y = b.y - 20

                    sendData = json.dumps(prevData)
                    conn.sendall(str.encode(sendData))

    except (Exception) as err:
        print('Connection Error : ' + str(err))
        conn.close()
    finally:
        print("Connection Closed")
        conn.close()

while True:
    try :
        conn, addr = s.accept()
        print("Connected to: ", addr)

        start_new_thread(threaded_client, (conn,))
    except (Exception) as exc:
        print('MAIN EXCEPTION :\n' + str(exc))