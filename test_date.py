import datetime

date = datetime.datetime.now()
print(date)

x = str(date)

print(x)

new_str = x.replace(" ", "_")
new_str = new_str.replace(":", "_")
new_str = new_str.replace(".", "_")

print(new_str)
