"""
A graphical user interface for the calculator
To open, instantiate the 'Window' class and then call the 'run' method
"""

import pygame as pg
from PygameTools import COLOURS, Draw, format_text
from Interface import Interface
from Errors import CalcError

class Window:

    def __init__(self):

        # constants
        self.__RESOLUTION = self.__WIDTH, self.__HEIGHT = 800, 600
        self.__TARGET_FPS = 30
        self.__BACKGROUND_COLOUR = COLOURS["grey"]
        self.__FONT = "freesansbold.ttf"

        # variables needed for the calculator
        self.__calculator = Interface()
        self.__expr = self.__ans = self.__error_msg = ""

        # the current mode name and mapping between mode names and their methods
        self.__mode = "normal"
        self.__modes = {
            "normal": self.__mode_normal,
            "instructions": self.__mode_instructions
        }

        # the distance the instructions scrollable view is positioned above the top of the screen
        self.__scroll = 0

        # whether or not to exit the calculator
        self.__done = False

    def run(self):
        """Run the calculator user interface"""

        # start pygame, create the window, caption it and start the clock
        pg.init()
        self.__display = pg.display.set_mode(self.__RESOLUTION)
        pg.display.set_caption("Calculator")
        clock = pg.time.Clock()

        # create my drawer for drawing things on the screen
        self.__drawer = Draw(self.__display, self.__FONT)

        # create buttons and text I will draw later
        self.__button_instructions = self.__drawer.button((0, 0, 200, 50), COLOURS["yellow"], "Instructions", 25, COLOURS["black"])
        self.__button_clear_memory = self.__drawer.button((200, 0, 200, 50), COLOURS["red"], "Clear Memory", 25, COLOURS["black"])
        self.__button_back = self.__drawer.button((self.__WIDTH - 100, 0, 100, 50), COLOURS["black"], "Back", 25, COLOURS["white"])
        self.__texts_expr = []
        self.__texts_ans = []
        self.__texts_error_msg = []
        self.__text_instructions_title = self.__drawer.text("Instructions", 25, COLOURS["yellow"], (400, 50))
        self.__text_memory = self.__drawer.text("Memory", 25, COLOURS["green"], (700, 50))
        self.__buttons_memory = []
        self.__text_extra_memory = []
        self.__format_instructions()

        # main loop
        while not self.__done:

            # clear screen
            self.__display.fill(self.__BACKGROUND_COLOUR)

            # get events
            events = pg.event.get()

            # let windows close the window
            for event in events:
                if event.type == pg.QUIT:
                    self.__done = True

            if not self.__done:

                # call the current mode's method
                self.__modes[self.__mode](events)

                # update the display and tick the clock
                pg.display.update()
                clock.tick(self.__TARGET_FPS)

        # close the pygame window
        pg.quit()

    def __mode_normal(self, events):
        """Runs every tick when in normal mode"""

        # draw buttons and text
        self.__button_instructions.draw()
        self.__button_clear_memory.draw()
        self.__text_memory.draw()
        for button in self.__buttons_memory:
            button.draw()
        for text in self.__texts_expr + self.__texts_ans + self.__texts_error_msg + self.__text_extra_memory:
            text.draw()

        # draw lines between the buttons to distinguish them (same colour as background so when they aren't there it looks the same)
        for count in range(2, 5+1):
            pg.draw.line(self.__display, self.__BACKGROUND_COLOUR, (600, 100 * count), (800, 100 * count))

        # handle events
        for event in events:
            if event.type == pg.KEYDOWN:

                # if the user pressed escape, clear the expression
                if event.key == pg.K_ESCAPE:
                    self.__expr = ""
                    self.__update_text_and_buttons(expr=True)

                # if the user presses backspace, remove 1 character from the expression
                elif event.key == pg.K_BACKSPACE:
                    self.__expr = self.__expr[:-1]
                    self.__update_text_and_buttons(expr=True)

                # if either or the return/enter keys are pressed, call the 'calculate' method
                elif event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                    self.__calculate()

                # otherwise add the text to the expression
                else:

                    # if the first thing they type isn't a number or a letter, insert the last answer into the start of the expression
                    if event.key not in [pg.K_0, pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9, pg.K_KP0, pg.K_KP1, pg.K_KP2, pg.K_KP3, pg.K_KP4, pg.K_KP5, pg.K_KP6, pg.K_KP7, pg.K_KP8, pg.K_KP9, pg.K_a, pg.K_b, pg.K_c, pg.K_d, pg.K_e, pg.K_f, pg.K_g, pg.K_h, pg.K_i, pg.K_j, pg.K_k, pg.K_l, pg.K_m, pg.K_n, pg.K_o, pg.K_p, pg.K_q, pg.K_r, pg.K_s, pg.K_t, pg.K_u, pg.K_v, pg.K_w, pg.K_x, pg.K_y, pg.K_z] and self.__expr == "":
                        self.__expr = self.__ans

                    self.__ans = self.__error_msg = ""
                    self.__expr += event.unicode
                    self.__update_text_and_buttons(expr=True, ans=True, error=True)

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pg.mouse.get_pos()

                # if the user clicked the instructions button, change to instructions mode
                if self.__button_instructions.is_within(mouse_pos):
                    self.__mode = "instructions"

                # if the user clicked the clear memory button, clear the memory
                elif self.__button_clear_memory.is_within(mouse_pos):
                    self.__calculator.clear_memory()
                    self.__ans = self.__error_msg = ""
                    self.__update_text_and_buttons(memory=True, ans=True, error=True)

                # if the user clicked on a memory item, insert that item into the expression
                else:
                    for button in self.__buttons_memory:
                        if button.is_within(mouse_pos):
                            self.__expr += "M{}".format(self.__buttons_memory.index(button) + 1)
                            self.__update_text_and_buttons(expr=True)

    def __mode_instructions(self, events):
        """Runs every tick when in instructions mode"""

        # draw the instructions text onto the intemediate surface
        for line in self.__texts_instructions:
            line.draw()

        # draw the intemediate surface onto the main surface
        self.__display.blit(self.__intermediate, (0, 100 + self.__scroll))

        # draw a rectangle, the title and back button over the top of the top of the surface
        pg.draw.rect(self.__display, self.__BACKGROUND_COLOUR, (0, 0, self.__WIDTH, 100))
        self.__text_instructions_title.draw()
        self.__button_back.draw()

        # handle events
        for event in events:

            # if the user pressed escape or clicked the back button, change to normal mode
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.__mode = "normal"
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pg.mouse.get_pos()
                    if self.__button_back.is_within(mouse_pos):
                        self.__mode = "normal"

                # if the user scrolled up, lower the intemediate surface but not lower than the origin
                elif event.button == 4:
                    self.__scroll = min(self.__scroll + 15, 0)

                # if the user scrolled down, raise the intemediate surface but not higher than the point
                # where the bottom instructions line is fully visible
                elif event.button == 5:
                    self.__scroll = max(self.__scroll - 15, self.__HEIGHT - len(self.__texts_instructions) * 20 - 100)

    def __clean_up_expr(self, expr):
        """Remove whitespace and extra brackets on the outside of the expression"""

        expr = expr.strip()
        if len(expr) > 0:
            while expr[0] == "(" and expr[-1] == ")":
                expr = expr[1:-1].strip()

        return expr

    def __calculate(self):
        """Calculate the answer to the expression and update everything"""

        # remove whitespace at the start and end, make lower case and replace 'ans' with 'm1'
        expr = self.__expr.strip().lower().replace("ans", "m1")

        # replace all memory references with the actual answers, clean up the expression and call
        # the main calculator with the resulting expression, catching errors and displaying them
        try:
            self.__ans = self.__calculator.calculate(self.__clean_up_expr(self.__convert_memory_references(expr)))
        except CalcError as e:
            self.__error_msg = str(e)
            self.__ans = ""
            self.__update_text_and_buttons(ans=True, error=True)
        else:
            self.__error_msg = ""
            self.__expr = ""
            self.__update_text_and_buttons(True, True, True, True)

    def __convert_memory_references(self, expr):
        """Convert all memory references to the actual answers"""

        # runs for every 'm' in 'expr'
        for _ in range(expr.count("m")):

            # get the string after the first 'm'
            index = expr.split("m")[1]

            # find the number of characters until the first non-numerical character
            pos = 0
            while pos < len(index) and index[pos] in "0123456789":
                pos += 1

            # find the string between the first 'm' and the first non-numerical characters
            # the slice means all characters up to pos characters through it
            index = index[:pos]

            # if there is a number after the 'm':
            if index != "":
                index = int(index)

                # if valid, replace the reference with the actual answer
                if 1 <= index <= self.__calculator.len_memory():
                    expr = expr.replace("m{}".format(index), "(" + self.__calculator.memory_item(index)[1] + ")", 1)

                # otherwise, give an error message
                else:
                    raise CalcError("Memory references must be between 1 and the number of items in memory")

        return expr

    def __update_text_and_buttons(self, memory=False, expr=False, ans=False, error=False):
        """
        Update the message on text and button objects if the message has changed
        The parameters are whether or not to update the message on those text/button objects
        """

        # if we need to update the memory buttons:
        if memory:

            self.__text_extra_memory = []
            count = 0

            # for the most recent 5 items in memory:
            for expression, answer in self.__calculator.recent_memory(5):

                # format the text for each memory item into lines
                lines = format_text("{}: {} ({})".format(count + 1, answer, expression), 15, 3, True)

                # if there is only 1 line, make it
                if len(lines) == 1:

                    # if there is already a button, change the text
                    if len(self.__buttons_memory) > count:
                        self.__buttons_memory[count].edit_text_message(lines[0])

                    # otherwise create a button with the new text
                    else:
                        self.__buttons_memory.append(self.__drawer.button((600, 100 * (count + 1), 200, 100), COLOURS["black"], lines[0], 20, COLOURS["white"]))

                # otherwise make it and add the other 1 or 2 lines
                else:
                    # if there is already a button, change the text
                    if len(self.__buttons_memory) > count:
                        self.__buttons_memory[count].edit_text_message(lines[1])

                    # otherwise create a button with the new text
                    else:
                        self.__buttons_memory.append(self.__drawer.button((600, 100 * (count + 1), 200, 100), COLOURS["black"], lines[1], 20, COLOURS["white"]))

                    # add the first line
                    self.__text_extra_memory.append(self.__drawer.text(lines[0], 20, COLOURS["white"], (700, (100 * count) + 125)))

                    # if there are 3 lines, add this too
                    if len(lines) == 3:
                        self.__text_extra_memory.append(self.__drawer.text(lines[2], 20, COLOURS["white"], (700, (100 * count) + 175)))

                count += 1

            # remove buttons that aren't in memory anymore
            self.__buttons_memory = self.__buttons_memory[:count]

        # if we need to update the expression text objects:
        if expr:

            # format the expression into lines
            lines = format_text(self.__expr, 18, 5, True)
            count = 0
            for line in lines:

                # if there are already enough objects, change the message on it
                if len(self.__texts_expr) > count:
                    self.__texts_expr[count].edit_text_message(line)

                # otherwise, create a new object with the message
                else:
                    self.__texts_expr.append(self.__drawer.text(line, 35, COLOURS["blue"], (300, 200 + (30 * count))))

                count += 1

            # remove unnecessary objects
            self.__texts_expr = self.__texts_expr[:count]

        # if we need to update the answer text objects:
        if ans:

            # format the answer into lines
            lines = format_text(self.__ans, 18, 5, True)
            count = 0
            for line in lines:

                # if there are already enough objects, change the message on it
                if len(self.__texts_ans) > count:
                    self.__texts_ans[count].edit_text_message(line)

                # otherwise, create a new object with the message
                else:
                    self.__texts_ans.append(self.__drawer.text(line, 35, COLOURS["green"], (300, 400 + (30 * count))))

                count += 1

            # remove unnecessary objects
            self.__texts_ans = self.__texts_ans[:count]

        # if we need to update the error text objects:
        if error:

            # format the error message into lines
            lines = format_text(self.__error_msg, 40, 3)
            count = 0
            for line in lines:

                # if there are already enough objects, change the message on it
                if len(self.__texts_error_msg) > count:
                    self.__texts_error_msg[count].edit_text_message(line)

                # otherwise, create a new object with the message
                else:
                    self.__texts_error_msg.append(self.__drawer.text(line, 25, COLOURS["red"], (300, 100 + (25 * count))))

                count += 1

            # remove unnecessary objects
            self.__texts_error_msg = self.__texts_error_msg[:count]

    def __format_instructions(self):
        """Format the instructions into lines on a scrollable surface"""

        # extend the instructions
        instructions = "SCROLL DOWN TO VIEW MORE:\n\n" + self.__calculator.instructions + "\n\nTo insert a previous answer into the expression, click on the item in the memory section. You can also type 'ans' to insert the last answer into the expression or 'Mx' to insert the xth answer into the expression.\n\nYou can press ESCAPE at any time to clear the expression and when you start typing on an empty expression it will add the previous answer before it unless you type a number of just pressed ESCAPE."

        # format the instructions into lines
        lines = format_text(instructions, 75)

        # make the intemediate surface just bit enough to hold all the instruction lines and make it the background colour
        self.__intermediate = pg.surface.Surface((self.__WIDTH, len(lines) * 20 + 10))
        self.__intermediate.fill(self.__BACKGROUND_COLOUR)

        # make a new drawer to draw on the intemediate surface
        new_drawer = Draw(self.__intermediate, self.__FONT)

        # create a text object for each line
        self.__texts_instructions = []
        count = 0
        for line in lines:
            self.__texts_instructions.append(new_drawer.text(line, 20, COLOURS["black"], (400, 10 + 20 * count)))
            count += 1

if __name__ == "__main__":
    Window().run()
