from multiprocessing import Process
import os


def info(title):
    print(title)
    print('process id:', os.getpid())


def f(name):

    while True:
        info('function f')
        print('hello', name)


if __name__ == '__main__':
    info('main line')
    p = Process(target=f, args=('bob',))
    l = Process(target=f, args=('rui',))
    p.start()
    l.start()
    p.join()
    l.join()
