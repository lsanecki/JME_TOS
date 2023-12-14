from Library.process_test import *


def main():
    process_test = ProcessTest('Mercury_TS')
    # process_test.start()
    process_test.start_initialization()
    process_test.start_test()
    process_test.start_finalization()


if __name__ == '__main__':
    main()
