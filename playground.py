from enum import Enum
import scripts
import json
import uuid
from common import TimeMeasurement

class TestClass(object):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def __str__(self):
        return '({0}, {1})'.format(self.first, self.second)


class TestClass2(object):
    def __init__(self, value):
        self.value = value

    def run(self, triple):
        pass

    def process_run(self, i):
        print(i)


def run_test(line, **kwargs):
    scripts.parse_script_line(line)
    print(kwargs['object'])


class Ex1(Exception):
    def __init__(self, message, *args):
        self.message = message.format(*args)

    def __str__(self):
        return self.message


class Ex2(Ex1):
    pass


def enumcall():
    return enumerator(2)


def enumerator(par):
    for i in range(10):
        if i < par:
            print(i)
            yield i


class TestEnum(Enum):
    AA = 0
    BB = 1
    DD = 2
    CC = 3


if __name__ == '__main__':
    tm = TimeMeasurement.start("all")
    run_test('[PUT] <bottle> (1) <table> (1)', object='a', subject='b')
    s = '{"second": "one", "first": 1}'
    d = json.loads(s, object_hook=lambda d: TestClass(**d))
    print(d)
    cl2 = TestClass2(123)
    try:
        cl2.run((1, 2, TestClass2.process_run))
        raise Ex2("ex2 {0}-{1}", 1, 5)
    except Ex2 as e2:
        print(e2.message)
    except Ex1 as e1:
        print(e1.message)
    for j in enumcall():
        print('enumed {0}'.format(j))
    if next(enumerator(-2), None) is None:
        print('Empty')

    TimeMeasurement.stop(tm)
    tm = TimeMeasurement.start("all")
    res = TimeMeasurement.measure_function('Add', lambda: 1 + 1)
    print(res)
    print(list(TestEnum))
    print(uuid.uuid4())
    TimeMeasurement.stop(tm)
    print(TimeMeasurement.result_string())
    x = (1, 2)
    x += (3, 4)
    print(x)
