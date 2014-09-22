#!/usr/bin/env python3

import edanode
from midas.dispatcher import Dispatcher
import midas.utilities as mu
from gsrstream import GSRData


#                       1. Start EDA LSL-Stream
# -----------------------------------------------------------------------------
gsr_stream = GSRData(ch_count=1,srate=125,stream_name="gsr_stream")
gsr_stream.start()
# -----------------------------------------------------------------------------


#                       2. Start EDA-node
# -----------------------------------------------------------------------------
eda_cfg = mu.parse_config_to_dict("edanode.ini","edanode")
eda_node = edanode.EDANode(eda_cfg)
eda_node.start()
# -----------------------------------------------------------------------------

#                       3. Start dispatcher
# -----------------------------------------------------------------------------
dis_cfg = mu.parse_config_to_dict("edanode.ini","dispatcher")
dis = Dispatcher(dis_cfg)
dis.start()
# -----------------------------------------------------------------------------


# Cleanup
eda_node.stop()
eda_stream.stop()
