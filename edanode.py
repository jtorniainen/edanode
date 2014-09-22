#!/usr/bin/env python3

import sys
import time
from midas.node import BaseNode
from midas import pylsl_python3 as lsl
from midas import utilities as mu
import numpy as np

class EDANode(BaseNode):

    def __init__(self,*args):
        super().__init__(*args)

        self.metric_functions = []
        self.metric_functions.append(self.normalize_scl)
        self.generate_metric_lists()

        self.process_list.append(self.compute_scl)

    def normalize_scl(self,x):
        """ Returns the current SCL value normalized between 0 and 1. """
        max_val = np.max(x['data'][0])
        last_val = x['data'][0][-1]
        return last_val/max_val

    def compute_scl(self):
        """ Update secondary (SCL) data buffer with processed GSR values. """
        
        # We can initialize run-once stuff here
        interval = 5.0      # time between samples
        c = 0               # channel index

        # ----------- Process loop for acquiring secondary data ---------------
        i = 0
        while self.run_state.value:

            # 1. Snapshot current data buffer (last 90 seconds)
            data,times = self.data_snapshot([90, 90])

            # 2. Calculate the desired metric and grab the current time-stamp
            if len(data[0])>0:
                val = np.mean(data[0])
            else:
                val = 0
            tme = lsl.local_clock()

            # 3. Update secondary buffer            
            self.lock_secondary.acquire()
            self.channel_data_secondary[c][self.writepointer_secondary[c]] = val
            self.time_array_secondary[c][self.writepointer_secondary[c]] = tme
            i+= 1
            self.writepointer_secondary[c] = i % self.buffer_size_secondary
            self.lock_secondary.release()
            
            if ((0 == self.buffer_full_secondary[c]) and 
                                        (i >= self.buffer_size_secondary)):
                self.buffer_full_secondary[c] = 1

            # 4. Sleep until its time to calculate another value 
            time.sleep(interval)
        # ---------------------------------------------------------------------


if __name__ == '__main__':
    node = mu.midas_parse_config(EDANode,sys.argv)

    if node is not None:
        node.start()
        node.show_ui()
