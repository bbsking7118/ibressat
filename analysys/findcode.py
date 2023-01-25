import pandas as pd
import os

aPath = "E:/work/Python/pykiwoom/analysys/xls/"
os.chdir(aPath)
flist = os.listdir()
print(flist)
xlsx_list = [x for x in flist if x.endswith('.xlsx')]
close_data = []

for xls in xlsx_list:
    code = xls.split('.')[0]
    df = pd.read_excel(xls)
    df2 = df[['일자', '현재가']].copy()
    print(df2)
    df2.rename(columns={'현재가': code}, inplace=True)
    df2 = df2.set_index('일자')
    df2 = df2[::-1]
    close_data.append(df2)

# concat
df = pd.concat(close_data, axis=1)
df.to_excel("E:/work/Python/pykiwoom/analysys/output/"+"merge.xlsx")