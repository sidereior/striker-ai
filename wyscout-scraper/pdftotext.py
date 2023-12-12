import tabula
import os
# read PDF file
talbes = tabula.read_pdf("data/test2.pdf", pages="all")

# Table stats are hard-coded for now, update this as wyscout updates
""" 
Player
Minutes
played Goals / xG Assists / xA
Actions /
successful
Shots /
on target
Passes /
accurate
Crosses /
accurate
Dribbles /
successful
Duels /
won
Losses /
own half
Recoveries /
opponent half
Touches in
penalty area Offsides
Yellow /
Red cards
"""


# save them in a folder
folder_name = "tables"
if not os.path.isdir(folder_name):
    os.mkdir(folder_name)
# convert all tables of a PDF file into a single CSV file
# supported output_formats are "csv", "json" or "tsv"
tabula.convert_into("data/test2.pdf", "boston3.csv", output_format="csv", pages="all")


import os
import tabula
import pandas as pd

folder_name = "data"
if not os.path.isdir(folder_name):
    os.mkdir(folder_name)

# convert all tables of a PDF file into a single CSV file
csv_file = "boston3.csv"
tabula.convert_into("data/test2.pdf", csv_file, output_format="csv", pages="all")

# read the CSV file
df = pd.read_csv(csv_file)

# extract headers and convert them to string
headers = df.head()
headers = df.columns.tolist()
headers_string = ", ".join(headers)

# write headers to output.txt
with open("output.txt", "w") as file:
    file.write(headers_string)

#print("Headers saved to output.txt")


import re



# Provided data
data = """
Passing
MinutesForward passes /Back passes /Lateral passes /Short + mediumLong passes /Progressive passes /Passes to finalThrough passes /DeepKeySecond /ShotAverage pass
Playerplayedaccurateaccurateaccuratepasses / accurateaccurateaccuratethird / accurateaccuratecompletionspassesthird assistsassistslength
2A. Daley98'18/15
83%7/6
86%9/8
89%33/31
94%3/1
33%6/5
83%8/7
88%-1---17.8
5A. Lopez98'19/12
63%3/3
100%11/10
91%25/22
88%8/3
38%7/5
71%4/1
25%1/0
0%1---27.9
3K. Acito98'20/18
90%2/2
100%23/23
100%42/42
100%6/4
67%7/6
86%8/7
88%-2--121.7
12R. Mesalles80'17/11
65%11/10
91%19/15
79%31/26
84%12/8
67%11/6
55%6/4
67%-12-321.9
23K. Hot84'10/7
70%5/5
100%17/15
88%33/30
91%5/2
40%4/3
75%6/4
67%1/0
0%-1-219.9
6C. Kerr49'3/0
0%4/4
100%7/2
29%8/5
63%4/1
25%3/2
67%2/0
0%1/0
0%1---20.4
10N. Pariano91'14/10
71%10/9
90%14/10
71%36/29
81%5/3
60%10/5
50%3/2
67%----618.9
17W. Frederick91'10/6
60%1/1
100%14/14
100%26/22
85%2/1
50%6/6
100%5/5
100%-----18.8
9�. Bj�rnsson87'11/8
73%4/3
75%5/3
60%16/11
69%5/4
80%7/6
86%5/3
60%-----26.1
21F. Ajago87'3/0
0%5/3
60%5/3
60%15/10
67%-1/0
0%1/0
0%-12-117.2
8N. Bull J�rgensen37'3/1
33%-1/1
100%6/4
67%1/0
0%-------30.4
16L. Thomas18'5/2
40%3/3
100%4/4
100%8/7
88%3/1
33%3/3
100%1/0
0%--1-129.3
22D. Kerr43'5/3
60%3/3
100%4/2
50%16/12
75%1/0
0%-2/0
0%-22-214.3
25M. Ramirez18'3/2
67%1/1
100%4/4
100%9/8
89%--3/3
100%-1--112.3, Unnamed: 1, Unnamed: 2, Unnamed: 3, Unnamed: 4, Unnamed: 5, Unnamed: 6, Unnamed: 7, Unnamed: 8, Unnamed: 9, Unnamed: 10, Unnamed: 11, Unnamed: 12, Unnamed: 13, Unnamed: 14
"""

# Regex pattern to extract the relevant data
pattern = r"(\d+[A-Z]\. [A-Za-z�]+)\d+'\d+/\d+ \d+%(\d+/\d+ \d+%)?(\d+/\d+ \d+%)?(\d+/\d+ \d+%)?(\d+/\d+ \d+%)?(\d+/\d+ \d+%)?(\d+/\d+ \d+%)?(\d+/\d+ \d+%)?(-\d+)?-?(-\d+)?-?(-\d+)?-?(\d+\.\d+)"

# Applying regex to extract and format data
formatted_data = ';'.join([
    ','.join(filter(None, match)) 
    for match in re.findall(pattern, data)
])



print(formatted_data)




