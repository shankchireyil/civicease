from data_loader import run_import_cycle
from data_scrapper import run_scrapper
import time

hours_to_sleep = 1
while(True):
    run_scrapper()
    run_import_cycle()
    print("*"*50)
    print("Sleeping 1 hour till next refresh")
    print("*"*50)
    time.sleep(hours_to_sleep*3600)