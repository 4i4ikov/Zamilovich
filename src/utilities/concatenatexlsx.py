# import warnings
# import os
# import urllib3
# from datetime import datetime, time,date
from styleframe import StyleFrame
import pandas as pd
import logging
import glob
logging.basicConfig(format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.ERROR,
                    encoding="utf-8")
logger = logging.getLogger(__name__)
PATH = './POSTAVKI'
filenames = glob.glob(PATH + "/*.xlsx")
dataFrames = []
for file in filenames:
    try:
        dataFrames.append(pd.read_excel(file))
    except Exception as e: print (f'{file} + {e}')

big_frame = pd.concat(dataFrames, ignore_index=True)
# excelWriter = StyleFrame.ExcelWriter("concatinated.xlsx")
# styledDataFrame = StyleFrame(big_frame)
big_frame.to_excel("POSTAVKI.xlsx",index=False)
# styledDataFrame.to_excel(excel_writer=excelWriter,
#                         #  best_fit=(list(styledDataFrame.columns.values)),
#                            row_to_add_filters=0,index=False)
# excelWriter.close()