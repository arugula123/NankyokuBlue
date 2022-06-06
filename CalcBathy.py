#%%
# /usr/bin/python3 

'''
Calcurate of BlueROV observations to check observed bathymetry
For JARE64. @T.ISHIWA in NIPR.
'''

from base64 import encode
import cartopy.crs as ccrs

import glob
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import seaborn as sns

# Input Data
DIR = '/Users/ishiwa/Dropbox/01_DataArchive/NankyokuBlue/LakeShumarinai'  # データの格納場所

# Set Parameter
ANGLE = 10

'''
Seatrac: 位置決めのデータが格納。rawデータの拡張子はpplog。
    SeaTrac PinPointでcsvに変換したファイルが必要。
Sonarlog: BlueROVのデータ。深度情報を抜き出す。rawデータはCSVなので、ソフトウェアによる変換の必要なし。
Telemetry: 高度計のデータ。rawデータの拡張子はtlog。Mission Plannerで変換。
各ファイルは時刻で同期する。SonarLogのみGMT時刻なので、日本時刻に変換している。
'''

FileList = []
FileList = glob.glob(DIR+'/FormatData/SeaTrac/' + '*.csv')
with open('SeaTracCombined.csv', 'wb') as filenew:
    for file in FileList:
        with open(file, 'rb') as fileadd:
            filenew.write(fileadd.read())

FileList = []
FileList = glob.glob(DIR+'/RawData/SonarLog/' + '*.csv')
list = []
for file in FileList:
    list.append(pd.read_csv(file))
df = pd.concat(list)
df.to_csv('SonarLogCombined.csv',index=False)

FileList = []
FileList = glob.glob(DIR+'/FormatData/Telemetry/' + '*.txt')
with open('TelemetryCombined.txt', 'wb') as filenew:
    for file in FileList:
        with open(file, 'rb') as fileadd:
            filenew.write(fileadd.read())

Seatrac = './SeaTracCombined.csv'
Sonarlog = './SonarLogCombined.csv'
Telemetry = './TelemetryCombined.txt'

def SeatracCalc(Seatrac):
    # 位置データの抽出
    df0 = pd.read_csv(Seatrac,delimiter='[, ]',header=None,engine='python',encoding='shift-jis')

    df = df0.iloc[:,[4,1,2,3,6,7,10]]
    df.to_csv('tmp.txt',sep='\t',header=['Year','Month','Day','Time','Lat','Lon','DepthSeaTrac'],index=False)
    
    df = pd.read_csv('tmp.txt',sep='\t')

    df['TimeStamp'] = df['Year'].astype(int).astype(str) + df['Month'].astype(int).astype(str).str.zfill(2) \
        + df['Day'].astype(int).astype(str).str.zfill(2) + ' ' + df['Time']
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])

    df = df[['TimeStamp','Lat','Lon']].dropna()
    DATE = pd.to_datetime(df.loc[df.index[-1],'TimeStamp']).strftime('%Y/%m/%d')

    df.to_csv('SeaTrac.txt',sep='\t',index=False)

def SonarCalc(Sonarlog,Angle):
    # 深度データの抽出
    with open('tmp.txt','w') as outf:
        inf = open(Sonarlog,'r')
        for line in inf:
            line = re.sub(r'\s','',line.lstrip())
            print(line,file=outf,end='\n')

    df = pd.read_csv('tmp.txt',delimiter=',')

    # タイムゾーンの変換、TimeStampの作成
    df['TimeStamp'] = df['Date'] + ' ' + df['Time']
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'], format='%d/%m/%y %H:%M:%S')
    df['TimeStamp'] = df['TimeStamp'].dt.tz_localize('GMT')
    df['TimeStamp'] = df['TimeStamp'].dt.tz_convert('Asia/Tokyo')
    df['TimeStamp'] = df['TimeStamp'].dt.tz_localize(None)
    df = df[['TimeStamp','Distance(meters)','Heading','Roll','Pitch']]

    # df = df[(-30 <= df['Roll'] <= 30) & (-30 <= df['Pitch'] <= 30)]
    df = df[(df['Roll'] <= Angle) & (Angle * -1 <= df['Roll'])]
    df = df[(df['Pitch'] <= Angle) & (Angle *-1 <= df['Pitch'])]

    # 水深はROVの姿勢によらないので、同時刻データを平均値を採用
    df = df.groupby('TimeStamp').mean() # 重複した時間の値を平均
    # df = df.groupby('TimeStamp').min()     # 最小値

    df.to_csv('Sonar.txt',sep='\t')

def TelemetryCalc(Telemetry):
    # 高度データの抽出
    inf = open(Telemetry,'r')

    with open('tmp.txt','w') as outf:
        for line in inf:
            if 'mavlink_vfr_hud_t' in line:
                line = re.sub(r'\s+',' ',line.lstrip())
                print(line,file=outf,end='\n')

    df = pd.read_csv('tmp.txt',delimiter=' ',header=None)
    df.iloc[:,[0,1,16]].to_csv('tmp.txt',sep='\t',header=['Date','Time','Altitude'],index=False)

    df = pd.read_csv('tmp.txt',sep='\t')

    df['TimeStamp'] = df['Date'] + ' ' + df['Time']
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp'])

    # 水深はROVの姿勢によるので、同時刻データを最小値を採用
    df = df.groupby('TimeStamp').mean()     # 平均化
    df.to_csv('Telemetry.txt',sep='\t')

SeatracCalc(Seatrac)
SonarCalc(Sonarlog,ANGLE)
TelemetryCalc(Telemetry)

Seatrac = pd.read_csv('SeaTrac.txt',sep='\t')
Sonar = pd.read_csv('Sonar.txt',sep='\t')
Telemetry = pd.read_csv('Telemetry.txt',sep='\t')

tmp = pd.merge(Seatrac,Sonar,on='TimeStamp')
OUT = pd.merge(tmp,Telemetry,on='TimeStamp')
OUT = OUT.drop_duplicates()     # 重複データを削除
OUT.to_csv('MargeObs.txt',sep='\t',index=False)

fig = plt.figure(facecolor='white')

ax1 = fig.add_axes((0,0,1,0.8),xlabel='Longitiude',ylabel='Latitude',projection=ccrs.PlateCarree())
ax1.gridlines(crs=ccrs.PlateCarree(),draw_labels=True)
ax1.grid(color='k', linestyle=':',linewidth=0.5,alpha=0.8)
z = OUT['Altitude'] - OUT['Distance(meters)']
mappable = ax1.scatter(OUT['Lon'],OUT['Lat'],c=z,linewidths=0,alpha=0.5)
ax1.scatter(142.20,44.3049666667,marker='x')

fig.colorbar(mappable,ax=ax1,pad=0.15)

plt.savefig('map.png',format='png',dpi=300,bbox_inches='tight')

os.remove('tmp.txt')

exit()
# %%
