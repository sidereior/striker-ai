import tabula
import os
# read PDF file
tables = tabula.read_pdf("data/boston.pdf", pages="6,7")

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
tabula.convert_into("data/boston.pdf", "boston.csv", output_format="csv", pages="6,7")
