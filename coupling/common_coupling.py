counter = 1


class A:
    def increment_counter(self):
        global counter
        counter += 1


class B:
    def increment_counter(self):
        global counter
        counter += 1


def main():
    A().increment_counter()
    B().increment_counter()
