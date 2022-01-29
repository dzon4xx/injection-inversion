# So called pathological coupling :D
# HIGH COUPLING
class A:
    def __init__(self):
        self.prop = 1


class B:
    def change_a(self, a: A):
        # Content coupling
        a.prop += 1


def main():
    a = A()
    b = B()
    b.change_a(a)
