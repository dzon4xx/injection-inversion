class A:
    def __init__(self, data: dict):
        self._data = data

    def set_config(self):
        self._data["a"] = "abcd"

    def get_len(self):
        return len(self._data["a"])


class B:
    def __init__(self, data: dict):
        self._data = data

    def set_config(self):
        self._data["a"] = 1


def main():
    config = {"a": 2}
    a = A(config)
    b = B(config)

    a.set_config()
    a.get_len()
    b.set_config()
    a.get_len()

