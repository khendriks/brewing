from django.test import TestCase

from beer.models import Beer, Step

# Create your tests here.
from beer.utils import TreeTable


class UtilsTestCase(TestCase):
    class TestElement(object):
        def __init__(self, name, width):
            self.name = name
            self.width = width

        def get_width(self):
            return self.width

        def __repr__(self):
            return self.name

    def setUp(self):
        self.beer = Beer.objects.create(name="Beer")
        self.top = Step.objects.create(beer=self.beer, name="Top")
        self.a1 = Step.objects.create(beer=self.beer, parent=self.top, name="A1")
        self.a2 = Step.objects.create(beer=self.beer, parent=self.top, name="A2")
        self.a3 = Step.objects.create(beer=self.beer, parent=self.top, name="A3")
        self.b1 = Step.objects.create(beer=self.beer, parent=self.a1, name="B1")
        self.b3 = Step.objects.create(beer=self.beer, parent=self.a3, name="B3")
        self.b4 = Step.objects.create(beer=self.beer, parent=self.a3, name="B4")
        self.c3 = Step.objects.create(beer=self.beer, parent=self.b3, name="C3")

    def test_add_element(self):

        tree_table = TreeTable()
        top = self.TestElement("top", width=4)
        a1 = self.TestElement("a1", width=1)
        a2 = self.TestElement("a2", width=1)
        a3 = self.TestElement("a3", width=2)
        b1 = self.TestElement("b1", width=1)
        b3 = self.TestElement("b3", width=1)
        b4 = self.TestElement("b4", width=1)
        c3 = self.TestElement("c3", width=1)


        tree_table.add_element(top, 0, 0)
        expected = [[top, top, top, top]]
        self.assertEqual(str(expected), str(tree_table.rows))

        tree_table.add_element(a1, 0, 1)
        tree_table.add_element(a2, 1, 1)
        tree_table.add_element(a3, 2, 1)
        expected.append([a1, a2, a3, a3])
        self.assertEqual(str(expected), str(tree_table.rows))

        tree_table.add_element(b1, 0, 2)
        tree_table.add_element(b3, 2, 2)
        tree_table.add_element(b4, 3, 2)
        expected.append([b1, None, b3, b4])
        self.assertEqual(str(expected), str(tree_table.rows))

        tree_table.add_element(c3, 2, 3)
        expected.append([None, None, c3])

    def test_add_children(self):
        tree_table = TreeTable()
        tree_table.add_children_depth_first(self.top)
        expected = [[self.top, self.top, self.top, self.top],
                    [self.a1, self.a2, self.a3, self.a3],
                    [self.b1, None, self.b3, self.b4],
                    [None, None, self.c3]]
        self.assertEqual(str(expected), str(tree_table.rows))

    def test_get_row(self):
        tree_table = TreeTable()
        tree_table.add_children_depth_first(self.top)
        expected = [[self.top],
                    [self.a1, self.a2, self.a3],
                    [self.b1, TreeTable.EmptyCell(), self.b3, self.b4],
                    [TreeTable.EmptyCell(width=2), self.c3]]
        actual = tree_table.get_rows()
        self.assertEqual(str(expected), str(actual))
        for i in range(0, len(expected)):
            for j in range(0, len(expected[i])):
                self.assertEqual(expected[i][j].get_width(), actual[i][j].get_width())






