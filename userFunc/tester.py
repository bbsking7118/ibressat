import os, re
from datetime import date, datetime, timedelta
from time import sleep
import pandas as pd
import pyautogui

import json

def tester(parent, logger, *args,**kwargs):
    logger.debug("bsFunc(test_function) start...")
    today = datetime.today()
    diff_days = timedelta(days=30)
    print(today-diff_days)

if __name__ == "__main__":
    tester()