import dataclasses


# Inheritance  HIGH COUPLING
@dataclasses.dataclass
class A:
    a: int

    def foo(self):
        print(self.a)

    def biz(self):
        print("biz")


@dataclasses.dataclass
class B(A):
    b: int

    def bar(self):
        self.foo()


# Composition # LOW COUPLING
@dataclasses.dataclass
class C:
    a: int

    def foo(self):
        print(self.a)

    def biz(self):
        print("biz")


@dataclasses.dataclass
class D:
    c: C
    b: int

    def bar(self):
        self.c.foo()
