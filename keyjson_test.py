#coding=utf-8
from __future__ import absolute_import

from unittest import TestCase

if __name__ == "__main__" and __package__ is None:
    __package__ = "keyjson_test"

import keyjson
import keyjson_alt

IMPLS = [keyjson, keyjson_alt]


BYTESTRINGS = [
    '', '1', '12', '123', '1234', '12345', '123456',
    5 * ''.join(chr(i) for i in range(256)),
]

KEYJSON_EXAMPLES = [
    [None,                      '\x31'],
    [False,                     '\x32'],
    [True,                      '\x33'],
    [u"Montréal",               '\x34Montr\xC3\xA9al'],
    [[u"x", 0],                 '\x35\x34x\x00\xC0\x80'],
    [[u"x", 0, u"Foo"],         '\x35\x34x\x00\xC0\x80\x00\x34Foo'],
    [{u"x": 0, u"y": u"Foo"},   '\x36\x34x\x00\xC0\x80\x00\x34y\x00\x34Foo'],
    [-(128**2),                 '\xBD\xFE\xFF\xFF'],
    [-129,                      '\xBE\xFE\xFE'],
    [-128,                      '\xBE\xFE\xFF'],
    [-127,                      '\xBF\x80'],
    [-126,                      '\xBF\x81'],
    [-2,                        '\xBF\xFD'],
    [-1,                        '\xBF\xFE'],
    [0,                         '\xC0\x80'],
    [1,                         '\xC0\x81'],
    [126,                       '\xC0\xFE'],
    [127,                       '\xC0\xFF'],
    [128,                       '\xC1\x81\x80'],
    [129,                       '\xC1\x81\x81'],
    [128**2,                    '\xC2\x81\x80\x80'],
    [128**3,                    '\xC3\x81\x80\x80\x80'],
]


def check(impl, x, expected_y=None):
    
    y = impl.dumps(x)
    x2 = impl.loads(y)
    
    if (x != x2) or (expected_y is not None and y != expected_y):
        msg = '''
****************************
             x: %s
            x2: %s
            
                  f(x): %s
            expected_y: %s
****************************
        ''' % (
                repr(x),
                repr(x2),
                y.encode('hex'),
                expected_y.encode('hex') if expected_y else 'None')
        raise Exception(msg)



class TextBase64(TestCase):
    def runTest(self):
        for impl in IMPLS:
            for data in BYTESTRINGS:
                assert impl.b64decode(impl.b64encode(data)) == data


class TestExamples(TestCase):
    def runTest(self):
        for impl in IMPLS:
            for x, expected_y in KEYJSON_EXAMPLES:
                check(impl, x)


class TestKeyjsonExamples(TestCase):
    def runTest(self):
        for x, expected_y in KEYJSON_EXAMPLES:
            check(keyjson, x, expected_y=expected_y)



if __name__ == '__main__':
    import unittest
    unittest.main()
