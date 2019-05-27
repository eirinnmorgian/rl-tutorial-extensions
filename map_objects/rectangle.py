class Rect:
    '''
    helper class to create rooms
    '''
    def __init__(self, x, y, w, h):
        # bottom-left corner = (x1, y1)
        # top-right corner = (x2, y2)
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return (center_x, center_y)

    def intersects(self, other):
        # returns true if this rect intersects with another
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
