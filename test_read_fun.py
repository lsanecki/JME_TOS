import Liblary.deviceFun

print(dir(Liblary.deviceFun))

is_exist_fun = 'fun_a' in dir(Liblary.deviceFun)

print(is_exist_fun)

'''
item = getattr(Liblary.deviceFun, 'fun_a')
if callable(item):
    item()

item = getattr(Liblary.deviceFun, 'fun_b')
if callable(item):
    item('p1', 'p2', 'p3')
'''
param = ["param1", "param2", "param3"]

item = getattr(Liblary.deviceFun, 'fun_c')
if callable(item):
    item(param)

'''

def some_magic():
    import a
    for i in dir(a):
        item = getattr(a,i)
        if callable(item):
            item()

if __name__ == '__main__':
    some_magic()
'''
