"""
Tools for writing pygame windows
"""

import pygame as pg

COLOURS = {
    "black":    (0,    0,      0),
    "white":    (255,  255,    255),
    "grey":     (200,  200,    200),
    "red":      (255,  0,      0),
    "green":    (0,    200,    0),
    "blue":     (0,    0,      255),
    "yellow":   (255,  255,    0)
}

def format_text(text, MAX_CHARS_PER_LINE, MAX_LINES=None, break_anywhere=False):
    """Format text into lines so they fit on the screen and if it exceeds the maximum number of lines, trail off..."""

    # if we allow breaking the string anywhere, we just treat the string as an array of characters
    if break_anywhere:
        words = text

    # otherwise we split the text into an array of words (however we haven't dealt with newlines yet)
    else:
        words = text.split(" ")

    # initialise the new 'lines' list and 'current_line' string as empty
    lines = []
    current_line = ""

    # for each word in the instructions:
    word_num = 0
    while (MAX_LINES is None or len(lines) < MAX_LINES) and len(words) > word_num:
        word = words[word_num]

        # while there is a newline character in the current word:
        while "\n" in word:

            # the line is the word before the newline character
            line = word.split("\n")[0]

            # if it can't fit on the current line, add the current line and it as 2 separate lines
            if len(line) + len(current_line) > MAX_CHARS_PER_LINE:
                lines.append(current_line)
                lines.append(line)

            # if it can fit, add the word (add a space between if we don't allow breaking words anywhere)
            else:
                if break_anywhere:
                    lines.append(current_line + line)
                else:
                    lines.append(current_line + " " + line)

            # the current line is empty as after a newline character we always start a new line when there is a newline character
            current_line = ""

            # then replace the 'word' variable with all characters after the first newline character and continue the loop
            word = "\n".join(word.split("\n")[1:])

        # if there is enough room to put the word on the current line, add it
        # otherwise, add it to a new line
        if len(word) + len(current_line) > MAX_CHARS_PER_LINE:
            lines.append(current_line)
            current_line = word
        else:
            # only add a space if we don't allow breaking anywhere
            if break_anywhere:
                current_line += word
            else:
                current_line += " " + word

        word_num += 1

    # if we have run out of room, trail off
    if MAX_LINES is not None and len(lines) == MAX_LINES:
        lines[-1] += "..."

    # otherwise, add the last line
    else:
        lines.append(current_line)

    return lines

def middle_box(box):
    """Return the middle position of 'box'"""
    return box[0] + box[2] // 2, box[1] + box[3] // 2

class Text:
    """Text object facilitating drawing to the screen and changing the text message"""
    def __init__(self, text_message, size, colour, center_pos, font, display):
        self.__font = pg.font.Font(font, round(size))
        self.__colour = colour
        self.__center_pos = center_pos
        self.__display = display
        self.__surf = self.__font.render(str(text_message), True, colour)
        self.__rect = self.__surf.get_rect()
        self.__rect.center = center_pos
    def draw(self):
        """Draw the text to the display"""
        self.__display.blit(self.__surf, self.__rect)
    def edit_text_message(self, new_text_message):
        """Edit the text message"""
        self.__surf = self.__font.render(str(new_text_message), True, self.__colour)
        self.__rect = self.__surf.get_rect()
        self.__rect.center = self.__center_pos

class Button:
    """Button object facilitating drawing it and the text in it to the screen, checking whether a point lies within it and changing the text message on the box"""
    def __init__(self, box, colour, text, display):
        self.__box = box
        self.__colour = colour
        self.__text = text
        self.__display = display
    def draw(self):
        """Draw the button and text in it to the display"""
        pg.draw.rect(self.__display, self.__colour, self.__box)
        self.__text.draw()
    def is_within(self, mouse_pos):
        """Return whether or not the mouse is within the button"""
        return self.__box[0] <= mouse_pos[0] <= self.__box[0] + self.__box[2] and self.__box[1] <= mouse_pos[1] <= self.__box[1] + self.__box[3]
    def edit_text_message(self, new_text_message):
        """Edit the text message on the button"""
        self.__text.edit_text_message(new_text_message)

class Draw:
    """Drawer object which facilitates creating buttons and text in pygame"""
    def __init__(self, display, font):
        self.__display = display
        self.__font = font
    def button(self, box, box_colour, text_message, text_size, text_colour):
        """Create a button"""
        return Button(box, box_colour, self.text(text_message, text_size, text_colour, middle_box(box)), self.__display)
    def text(self, text_message, size, colour, center_pos):
        """Create text"""
        return Text(text_message, size, colour, center_pos, self.__font, self.__display)
