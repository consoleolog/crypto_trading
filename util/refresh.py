import os

import common_util

log_file = f"{os.getcwd()}/logs/crypto.log"

data_dir = f"{os.getcwd()}/data"

common_util.refresh_file({
    "log_file" : log_file,
    "data_dir" : data_dir
})
