import sys

with open('report/main.tex', 'rb') as f:
    lines = f.readlines()

with open('report/main.tex', 'wb') as f:
    for line in lines:
        if b'caption' in line and b'trung' in line:
            f.write(b'    \\caption{Th\xe1\xbb\x9di gian th\xe1\xbb\xb1c thi t\xe1\xba\xa1i $N=30$ (trung b\xc3\xacnh 3 l\xe1\xba\xa7n l\xe1\xba\xb7p), \xc4\x91\xc6\xa1n v\xe1\xbb\x8b gi\xc3\xa2y.}\r\n')
        else:
            f.write(line)
