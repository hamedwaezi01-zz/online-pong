# LOLOLOL

import turtle
import sys
from network import Network
import json
from json import JSONDecodeError
import yaml
import time


class Game:

    def __init__(self):

        print('connected')


        self.width = 800
        self.height = 600
        # self.ballDx = 0.09
        # self.ballDy = 0.1

        self.wn = turtle.Screen()
        self.wn.title("Pong By HamedWaezi01@gmail.com")
        self.wn.bgcolor("black")
        self.wn.setup(width=800, height=600)
        self.wn.tracer(0)

        # Score
        self.scoreA = 0
        self.scoreB = 0

        # Paddle A LEFT
        self.paddleA = turtle.Turtle()
        self.paddleA.speed(0)
        self.paddleA.shape("square")
        self.paddleA.color("red")
        self.paddleA.shapesize(stretch_len=1, stretch_wid=5)
        self.paddleA.penup()
        self.paddleA.goto(0.0625 * self.width - self.width / 2, 0)

        # Paddle B RIGHT
        self.paddleB = turtle.Turtle()
        self.paddleB.speed(0)
        self.paddleB.shape("square")
        self.paddleB.color("white")
        self.paddleB.shapesize(stretch_len=1, stretch_wid=5)
        self.paddleB.penup()
        self.paddleB.goto(self.width / 2 - 0.0625 * self.width, 0)

        # Pen
        self.pen = turtle.Turtle()
        self.pen.speed(0)
        self.pen.color("white")
        self.pen.penup()
        self.pen.hideturtle()
        self.pen.goto(0, 0.4333 * self.height)
        self.pen.write("Player A: 0 Player B: 0\t\t R -> RESET, X -> EXIT", align="center", font=('Courier', 15, 'normal'))

        # Ball
        self.ball = turtle.Turtle()
        self.ball.speed(0)
        self.ball.shape("square")
        self.ball.color("white")
        self.ball.penup()
        self.ball.goto(0, 0)

        # self.ball.dx = self.ballDx
        # self.ball.dy = self.ballDy

        self.paddleB.gotPoint = False
        self.paddleA.gotPoint = False

        self.ball.isMoving = True

        # Key Binding
        self.wn.listen()


        self.net = Network()
        self.isBallMoving = 1

        self.z = [False for i in range(6)]
        self.ctrl = -1

        # print("id : "+str(self.net.id))
        if self.net.id == 1:

            self.wn.onkeypress(self.paddleBUp, "Up")
            self.wn.onkeypress(self.paddleBDown, "Down")
        else:

            self.wn.onkeypress(self.paddleAUp, "w")
            self.wn.onkeypress(self.paddleADown, "s")
        self.wn.onkeypress(self.moveBall, "space")
        self.wn.onkeypress(self.resetGame, 'r')
        self.wn.onkeypress(self.endGame, 'x')
        self.exit = False


    def send_data(self, data):
        reply = self.net.send(data)
        return reply


    def parse_data(self, data):
       try:
          d = [float(i) for i in data.split(",")]
          return d
       except:
          return 0, 0

    # Functions
    def paddleAUp(self,):

        self.z[0] = True


    def paddleADown(self):

        self.z[1] = True


    def paddleBUp(self):
        self.z[2] = True


    def paddleBDown(self):
        self.z[3] = True


    def moveBall(self,):
        if self.isBallMoving == 0:
            self.z[4] = True

    def endGame(self):
        self.z[5] = True
        self.ctrl = 0

    def resetGame(self):
        self.z[5] = True
        self.ctrl = 1

    def exitGame(self):
        self.exit = True

    def run(self):
        # Event Loop

        while True:

            # print(str(self.ball.xcor()) + '  ' + str(self.ball.ycor()))
            self.wn.update()
            reply = {}
            if self.z[0]: # A UP
                reply = self.send_data(data=json.dumps({'a':'up', 'b': 'none', 'isBallMoving': self.isBallMoving,'space':-1, 'ctrl' : -1}))

            elif self.z[1]: # A DOWN
                reply = self.send_data(data=json.dumps({'a': 'down', 'b': 'none', 'isBallMoving': self.isBallMoving,'space':-1, 'ctrl' : -1}))

            elif self.z[2]: # B UP
                reply = self.send_data(data=json.dumps({'a': 'none', 'b': 'up', 'isBallMoving': self.isBallMoving,'space':-1, 'ctrl' : -1}))

            elif self.z[3]:
                reply = self.send_data(data=json.dumps({'a': 'none', 'b': 'down', 'isBallMoving': self.isBallMoving, 'space':-1, 'ctrl' : -1}))

            elif self.z[4]: # IF SPACE IS PRESSED
                d = {'a': 'none', 'b': 'none', 'isBallMoving': self.isBallMoving, 'space': int(self.net.id), 'ctrl' : -1}
                reply = self.send_data(data=json.dumps(d))

            elif self.z[5]: # EXIT or RESET
                reply = self.send_data(data=json.dumps({'a': 'none', 'b': 'none', 'isBallMoving': self.isBallMoving, 'space': -1, 'ctrl': self.ctrl}))

            else:
                reply = self.send_data(
                    data=json.dumps({'a': 'none', 'b': 'none', 'isBallMoving': self.isBallMoving,
                                     'space': -1, 'ctrl' : -1}))

            self.z = [False for i in range(6)]

            reply = yaml.load(reply)

            self.isBallMoving = reply.get('isBallMoving')
            if reply['close'] == 1:
                if reply['winner'] != -1:
                    winnerPen = turtle.Turtle()
                    winnerPen.speed(0)
                    winnerPen.color("white")
                    winnerPen.penup()
                    winnerPen.hideturtle()
                    winnerPen.goto(0, 0.2 * self.height)
                    winner = 'A' if reply['winner'] == 0 else 'B' if reply['winner'] == 1  else 'LOL'
                    self.pen.clear()
                    print("PLAYER {} WON THE GAME".format(winner))
                    self.wn.onkeypress(None, 'x')
                    self.wn.onkeypress(self.exitGame, 'x')
                    self.net.client.close()
                    while not self.exit:
                        winnerPen.clear()
                        winnerPen.write("PLAYER {} WON THE GAME\npress `X` to exit the game".format(winner),
                                        align="center", font=('Courier', 15, 'normal'))
                    break
                self.net.client.close()
                break


            # Moving Ball
            if self.isBallMoving:


                self.ball.setx(reply['ball.x'])
                self.ball.sety(reply['ball.y'])

            elif reply['a.gotPoint'] == 1:
               # print('A got point move ball')
               self.ball.goto(reply['b.x'] - 0.04 * self.width , reply['b.y']  + 0.01 * self.height)
            elif reply['b.gotPoint'] == 1:
               # print('B got point move ball')
               self.ball.goto(reply['a.x']  + 0.04 * self.width, reply['a.y']  + 0.01 * self.height)
            self.pen.clear()
            self.pen.write("Player A: {} Player B: {}\t\t R -> RESET, X -> EXIT".format(reply['scoreA'], reply['scoreB']), align="center", font=('Courier', 15, 'normal'))


            self.paddleA.sety(reply['a.y'])
            self.paddleA.setx(reply['a.x'])

            self.paddleB.setx(reply['b.x'])
            self.paddleB.sety(reply['b.y'])



game = Game()
game.run()
print('Game Ended')