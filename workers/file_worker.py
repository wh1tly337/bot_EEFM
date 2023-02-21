import os

from auxiliary.req_data import *


# TODO xlsx to csv/db and handle info function

def file_delete(filename):
    os.remove(f"{src_files}{filename}")

# TODO automatically date update in schedule_template function

# TODO add watch schedule on today and on week function
