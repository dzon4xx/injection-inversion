import dataclasses


# Inheritance  HIGH COUPLING
@dataclasses.dataclass
class Base1:
    a: int

    def foo(self):
        print(self.a)

    def biz(self):
        print("biz")


@dataclasses.dataclass
class A(Base1):
    b: int

    def bar(self):
        self.foo()


# Composition # LOW COUPLING
@dataclasses.dataclass
class Base2:
    a: int

    def foo(self):
        print(self.a)

    def biz(self):
        print("biz")


@dataclasses.dataclass
class A:
    base: Base2
    b: int

    def bar(self):
        self.base.foo()
