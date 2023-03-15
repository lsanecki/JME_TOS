from Library.process_test import *


def main():
    process_test = ProcessTest('Mercury_TS2')
    process_test.start()
    print(process_test.tester.name)


if __name__ == '__main__':
    main()
