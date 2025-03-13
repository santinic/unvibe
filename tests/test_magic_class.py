from dataclasses import dataclass
from unittest import TestCase

import unvibe
from unvibe import ai


class TestMagicClass(TestCase):
    def test_Node(self):
        @ai
        class Node:
            """A node of a binary tree."""

        impl = '''
class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        
    def arity(self):
        if self.left is None and self.right is None:
            return 0
        elif self.left is not None and self.right is not None:
            return 2
        else:
            return 1
        '''

        Node.set_impl(impl)
        node = Node(1)
        self.assertEqual(node.arity(), 0)
        node.left = Node(2)
        self.assertEqual(node.arity(), 1)
        node.right = Node(3)
        self.assertEqual(node.arity(), 2)

    def test_Complex(self):
        impl = '''
class Complex:
    def __init__(self, real=0, imag=0):
        if not isinstance(real, (int, float)) or not isinstance(imag, (int, float)):
            raise TypeError("Real and imaginary parts must be numbers")
        self.real = real
        self.imag = imag

    @property
    def conjugate(self):
        return Complex(self.real, -self.imag)

    @property
    def magnitude(self):
        return (self.real**2 + self.imag**2)**0.5

    def __str__(self):
        if self.imag >= 0:
            return f"{self.real}+{abs(self.imag)}j"
        else:
            return f"{self.real}{abs(self.imag)}j"

    def __add__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real + other.real, self.imag + other.imag)
        elif isinstance(other, (int, float)):
            return Complex(self.real + other, self.imag)
        else:
            raise TypeError("Unsupported operand type for +")

    def __sub__(self, other):
        if isinstance(other, Complex):
            return Complex(self.real - other.real, self.imag - other.imag)
        elif isinstance(other, (int, float)):
            return Complex(self.real - other, self.imag)
        else:
            raise TypeError("Unsupported operand type for -")

    def __mul__(self, other):
        if isinstance(other, Complex):
            real = (self.real * other.real) - (self.imag * other.imag)
            imag = (self.real * other.imag) + (self.imag * other.real)
            return Complex(real, imag)
        elif isinstance(other, (int, float)):
            real = self.real * other
            imag = self.imag * other
            return Complex(real, imag)
        else:
            raise TypeError("Unsupported operand type for *")

    def __truediv__(self, other):
        if isinstance(other, Complex):
            denominator = other.real**2 + other.imag**2
            real = (self.real * other.real) + (self.imag * other.imag)
            imag = (self.imag * other.real) - (self.real * other.imag)
            return Complex(real / denominator, imag / denominator)
        elif isinstance(other, (int, float)):
            if other == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            real = self.real / other
            imag = self.imag / other
            return Complex(real, imag)
        else:
            raise TypeError("Unsupported operand type for /")

    def __abs__(self):
        return self.magnitude
'''

        @ai
        class Complex:
            pass

        Complex.set_impl(impl)
        c1 = Complex(1, 2)
        self.assertEqual(c1.real, 1)
        self.assertEqual(c1.imag, 2)
        c2 = Complex(3, 4)
        result = c1 + c2
        self.assertEqual(result.real, 4)
        self.assertEqual(result.imag, 6)
