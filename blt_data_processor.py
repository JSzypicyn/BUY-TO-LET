import pandas as pd
import datetime
import os
# os.chdir('C:\Jovian\Python') update directory path if your running this on your local machine
import matplotlib.pyplot as plt
from datetime import date
import csv
import re
import glob
import numpy as np

filename = glob.glob("*_data.csv")[0]

def import_data():
    df = pd.read_csv(filename)
    return df

def look_for_yield_numbers(df):
    i = 0
    numbers_present = np.empty(len(df))

    for i, desc in enumerate(df["Description"]):

        D1 = re.findall('\\d+(?:\\.\\d+)?%', str(desc))
        D2 = re.findall(r'\d+pcm', str(desc))
        D3 = re.findall('\d+[\,\.]\d+\S* per annum', str(desc))
        D4 = re.findall('\d+[\,\.]\d+\S* p.a.', str(desc))
        A=np.array([D1,D2,D3,D4],dtype=object)
        if A.size != 0:
            print(A)


if __name__ == "__main__":
    print(filename)
    df = import_data()
    look_for_yield_numbers(df)
