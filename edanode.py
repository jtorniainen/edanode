#!/usr/bin/env python3

import sys
import time
from midas.node import BaseNode
from midas import pylsl_python3 as lsl
from midas import utilities as mu


class EDANode(BaseNode):

    def __init__(self,*args):
        super().__init__(*args)

        self.metric_functions = []
        self.metric_functions.append(self.infoload)
        self.generate_metric_lists()

        self.process_list.append(self.process_eda)

    def infoload(self,x):
        """ This is a place-holder. """
        print("ping")
        return 256

    def process_eda(self):
        """ Update secondary data buffer with processed EDA values. """
        
        # We can initialize run-once stuff here
        interval = 5.0;

        # ----------- Process loop for acquiring secondary data ---------------
        i = 0
        while self.run_state.value:

            # 1. Snapshot current data buffer (last 90 seconds)
            data,times = self.data_snapshot([90, 90])

            # 2. Calculate the desired metric and grab the current time-stamp
            val = len(data[0])
            tme = lsl.local_clock()

            # 3. Update secondary buffer            
            self.lock_secondary.acquire()
            self.channel_data_secondary[0][self.writepointer_secondary[0]] = val
            self.time_array_secondary[0][self.writepointer_secondary[0]] = tme
            i+= 1
            self.writepointer_secondary[0] = i % self.buffer_size_secondary
            self.lock_secondary.release()
            
            if ((0 == self.buffer_full_secondary[0]) and 
                                        (i >= self.buffer_size_secondary)):
                self.buffer_full_secondary[0] = 1

            # 4. Sleep until its time to calculate another value 
            time.sleep(interval)
        # ---------------------------------------------------------------------


if __name__ == '__main__':
    node = mu.midas_parse_config(EDANode,sys.argv)

    if node is not None:
        node.start()
        node.show_ui()
