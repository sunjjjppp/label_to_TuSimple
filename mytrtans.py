import json
import re
import numpy as np
import os
def multi_split(string, delimiters):
    regex_pattern = '|'.join(map(re.escape, delimiters))
    result = re.split(regex_pattern, string)
    return result
Data = []
with open("./label_data_0809.json") as inputData:
    for line in inputData:
        try:
            Data.append(json.loads(line.rstrip(';\n')))
        except ValueError:
            print ("Skipping invalid line {0}".format(repr(line)))
l = np.array(Data)
n = 0
delimiters = ["/", "."]
for i in l:
    dict_n = l[n]
    a11 = dict_n['lanes']
    b11 = dict_n['h_samples']
    c11 = dict_n['raw_file']
    result = multi_split(c11, delimiters)
    result1 = [i for num, i in enumerate(result) if num not in [0,1,3]]
    result1[0] = result1[0] + ".txt"
    h1 = []
    for num_road in range(0, len(a11)):
        h1.append([i1 for i1,x1 in enumerate(a11[num_road]) if x1==-2])
        a_cn = [i1 for num,i1 in enumerate(a11[num_road]) if num not in h1[num_road]]
        b_cn = [i1 for num,i1 in enumerate(b11) if num not in h1[num_road]]
        rn = [item for pair in zip(a_cn, b_cn) for item in pair]
        content_n = [str(x) for x in rn]
        content1_n = [s+".00000" for s in content_n]
        content1_n.append("\n")
        with open(result1[0], "a") as f:
            f.write(" ".join(content1_n))
    n = n+1