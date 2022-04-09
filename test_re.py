import re

line = '8,500元/月'
line = re.sub(r'\W', '', line)
print(line)
print(line[:-2])
print(int(line[:-2]))
print(type(int(line[:-2])))
