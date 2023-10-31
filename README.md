# dsa-tds-scraper
extracts data from topdrawersoccer for DSA labs
# Soccer Game Data Processor

## Overview
The Soccer Game Data Processor is a Python tool designed to parse, process, and analyze soccer game data from various divisions. It reads HTML source code files of soccer game results, extracts relevant information, and saves it in a structured CSV format. This tool is particularly useful for anyone interested in analyzing soccer game statistics, betting trends, or conducting any form of sports analytics.

## Features
- **Multiple Division Support**: Handles data from different soccer divisions including d1, d2, d3, naia, and njcaa.
- **Batch Processing**: Option to process data in batches, creating separate files for each week and division.
- **Unbatched Processing**: Option to consolidate all data into a single CSV file.
- **Logging**: Comprehensive logging of warnings and errors for troubleshooting and data integrity assurance.
- **Customizable Output**: Allows users to specify the division and whether they prefer batched or unbatched output.

## Requirements
- Python 3.x
- Pandas
- lxml
- argparse

## Installation
1. Ensure that Python 3.x is installed on your system. You can download it from [Python's official website](https://www.python.org/downloads/).
2. Clone the repository or download the source code to your local machine.
3. Navigate to the project directory in your terminal or command prompt.
4. Install the required packages by running: `pip install -r requirements.txt`

## Usage
Navigate to the project directory in your terminal or command prompt, and run the script using the following command format:

``` python processing.py <division> <batched> ```
- <division>: The soccer division you want to process. Choose from:
    - d1: Division 1
    - d2: Division 2
    - d3: Division 3
    - naia: NAIA
    - njcaa: NJCAA
    - all: All divisions

<batched>:
True: Output in batched format (separate files for each week and division).
False: All data consolidated in a single file.

# How to run
Process all weeks and divisions, and save in batched format:
``` python processing.py all True ```
Process all weeks of division d1, and save in a single file:

```python processing.py d1 False```
Output
The processed data is saved in the outputs directory. The naming convention of the output files depends on your specified options:

Batched: <division>_week<week_number>_data_batch_<batch_id>.csv
Unbatched: <division>_unbatched_<batch_id>.csv for specific divisions or all_unbatched_<batch_id>.csv for all divisions.
Each CSV file contains the following columns:

Home Team
Away Team
Home Goals
Away Goals
Home Team Conference
Away Team Conference
Week
Division
