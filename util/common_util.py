import os

import pandas as pd


def refresh_file(inputs):
    os.remove(inputs['log_file'])
    for f in os.listdir(inputs['data_dir']):
        if f.endswith('.csv'):
            fp = os.path.join(inputs['data_dir'], f)
            ed = pd.DataFrame(columns=pd.read_csv(fp).columns)
            ed.to_csv(fp, index=False)