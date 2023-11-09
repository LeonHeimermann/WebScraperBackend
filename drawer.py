import turtle

from PIL import ImageGrab

scale_draw = 20


def test():
    turtle.speed(0)
    turtle.delay(0)

    goto_penup(0, 0)

    turtle.forward(20)
    turtle.left(90)
    turtle.forward(20)

    goto_penup(0, 0)
    turtle.done()


def draw(start_element):
    window = turtle.Screen()
    turtle.speed(0)
    turtle.delay(0)
    turtle.screensize(100000, 100000, 'white')

    goto_penup(0, 0)

    draw_tree_depth_first(start_element, 0)

    goto_penup(0, 0)
    turtle.done()
    turtle.bye()


def draw_tree_depth_first(current_element, depth):
    turtle.write(current_element.name, align="center", font=("Arial", 16, "normal"))
    turtle.forward(scale_draw)
    child_list = current_element.find_all(recursive=False)
    if len(child_list) > 0:
        turtle.right(90)
        turtle.forward(scale_draw)
        turtle.left(90)
        for child in child_list:
            draw_tree_depth_first(child, depth + 1)
        turtle.left(90)
        turtle.forward(scale_draw)
        turtle.right(90)


def goto_penup(x, y):
    turtle.penup()
    turtle.goto(x, y)
    turtle.pendown()
