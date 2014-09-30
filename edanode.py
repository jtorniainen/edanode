#!/usr/bin/env python3

import sys
import time
from midas.node import BaseNode
from midas import pylsl_python3 as lsl
from midas import utilities as mu
import numpy as np

class EDANode(BaseNode):
    """ Node for analyzing EDA-data. """

    def __init__(self,*args):
        """ Initialize EDA-node. """
        super().__init__(*args)

        self.metric_functions.append(self.normalize_scl)
        self.process_list.append(self.compute_scl)

    def normalize_scl(self,x):
        """ Returns the current SCL value normalized between 0 and 1. """
        max_val = np.max(x['data'][0])
        last_val = x['data'][0][-1]
        return last_val/max_val

    def compute_scl(self):
        """ Update secondary (SCL) data buffer with processed GSR values. """
        
        # We can initialize run-once stuff here
        interval = 5.0          # time between samples
        ch = 0                  # channel index

        # ----------- Process loop for acquiring secondary data ---------------
        while self.run_state.value:

            # 1. Snapshot current data buffer (last 90 seconds)
            data,times = self.data_snapshot([90, 90])

            # 2. Calculate the desired metric and grab the current time-stamp
            if len(data[0])>0:
                new_value = np.mean(data[0])
            else:
                new_value = 0
            time_stamp = lsl.local_clock()

            # 3. Update secondary buffer          
            self.push_sample_secondary(ch,time_stamp,new_value) 

            # 4. Sleep until its time to calculate another value 
            time.sleep(interval)
        # ---------------------------------------------------------------------


if __name__ == '__main__':
    node = mu.midas_parse_config(EDANode,sys.argv)

    if node is not None:
        node.start()
        node.show_ui()
