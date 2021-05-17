from graphics import *

def main():
    win = GraphWin('My window', 362, 500)
    win.setBackground(color_rgb(0, 0, 0))
    pt = Point(50, 50)
    cir = Circle(pt, 50)
    cir.setFill(color_rgb(255, 255, 255))
    cir.draw(win)
    img = Image(Point(181, 250), 'frontend/static/images/football_pitch_converted_resized.gif')
    img.draw(win)
    win.getMouse()
    win.close()

main()