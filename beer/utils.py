def is_staff(user):
    return user.is_staff and user.is_active

class TreeTable(object):

    def __init__(self, top=None):
        self.rows = []
        if top is not None:
            self.add_children_depth_first(top)

    def add_element(self, element, x, y):
        if len(self.rows) > y:
            row = self.rows[y]
        else:
            row =[]
            self.rows.append(row)

        # possibly add empty cells in front
        while len(row) < x:
            row.append(None)

        row.append(element)
        for i in range(0, element.get_width() - 1):
            row.append(element)

    def add_children_depth_first(self, element, start_x=0, depth=0):
        # add the element itself, then add the children
        self.add_element(element, start_x, depth)

        children = element.get_children()
        for child in sorted(children, key=step_sort, reverse=True):
            self.add_children_depth_first(child, start_x, depth+1)
            start_x += child.get_width()

    def get_rows(self):
        retList = []
        for row in self.rows:
            retRow = []
            i = 0
            while i < len(row):
                elem = row[i]
                if elem is not None:
                    # add the element to the return list
                    retRow.append(elem)
                    i += elem.get_width()
                else:
                    # add an empty element, or extend the previous one
                    if i == 0 or not isinstance(retRow[-1:][0], EmptyCell):
                        # add a new one, first column or the previous one is not an empty cell
                        retRow.append(EmptyCell())
                    else:
                        # extend the width of the previous empty cell
                        retRow[-1:][0].extend()
                    i += 1
            retList.append(retRow)
        return retList

def step_sort(step):
    child_depth = step.max_child_depth
    width = step.get_width()

    return child_depth, width


class EmptyCell(object):

    def __init__(self, width=1):
        self.width = width

    def get_width(self):
        return self.width

    def extend(self):
        self.width += 1

    def __repr__(self):
        return "EmptyCell ({0} width)".format(self.width)

    def __str__(self):
        return ""

    def __bool__(self):
        return False


