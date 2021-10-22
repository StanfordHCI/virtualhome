filename = "test.txt"

# with open(filename, 'r+') as f:
#     text = f.read()
#     text = re.sub('human', 'cat', text)
#     f.seek(0)
#     f.write(text)
#     f.truncate()
import fileinput
import sys

for line in fileinput.input(filename, inplace=1):
    if 'title' in line and '{{' not in line:
        line = line.replace('{', '{{')
        line = line.replace('}', '}}')
    sys.stdout.write(line)
x