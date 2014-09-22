import threading
from midas.node import lsl as pylsl
import uuid
import numpy


class GSRData(threading.Thread):
    """ Generates a stream which inputs randomly generated values into the LSL.

        Generates a multichannel stream which inputs random values into the LSL.
        Generated random values follow gaussian distribution where mean and 
        std values can be specified as arguments.
    """
    def __init__(self,stream_name="RANDOM",stream_type="RND",ch_count=3,
                 srate=128,mean=10,std=1,fmt='float32',nsamp=0):
        """ Initializes a data generator 
        
        Args:
            stream_name: <string> name of the stream in LSL (default="RANDOM")
            stream_type: <string> type of the stream in LSL (default="RND")
            ch_count: <integer> number of channels (default=3)
            srate: <integer> sampling rate (default=128)
            mean: <float> mean value for the random values (default=0)
            std: <float> standard deviation for the random values (default=1)
            fmt: <string> sample data format (default='float32')
            nsamp: <integer> number of samples in total (0=inf)
        """
        threading.Thread.__init__(self)

        # Stream stuff
        self.stream_name = stream_name
        self.stream_type = stream_type
        self.ch_count = ch_count
        self.srate = srate
        self.fmt = fmt
        self.uuid = str(uuid.uuid1())[0:4]

        # Synthetic data stuff, makes normally distributed noise for now
        self.data_mean = mean
        self.data_std = std

        # Setup timing related variables
        self.last_push = pylsl.local_clock()
        self.interval = 1.0/float(self.srate)
        if nsamp == 0:
            self.nsamp = numpy.inf
        else:
            self.nsamp = nsamp
        
        self.running = True
        
        # Outlet
        self.outlet = pylsl.StreamOutlet(pylsl.StreamInfo(self.stream_name,
                                                          self.stream_type,
                                                          self.ch_count,
                                                          self.srate,
                                                          self.fmt,
                                                          self.uuid))

    def set_srate(self,srate):
        """ Changes the sampling rate of the stream.

        Args:
            srate: <integer> new sampling rate 
        """
        self.srate = srate
        self.interval = 1.0 / float(self.srate)

    def set_mean(self,mean):
        """ Changes the mean of the random values.
    
        Args:
            mean: <float> new mean value for random samples
        """
        self.data_mean = mean

    def set_std(self,std):
        """ Changes the standard deviation of the random samples

        Args:
            std: <float> new standard deviation for random samples
        """
        self.data_std = std

    def push_sample(self):
        """ Pushes samples to LSL. """
        new_sample = []
        for n in range(0,self.ch_count):
            new_sample.append(numpy.random.normal(self.data_mean,self.data_std))
        self.outlet.push_sample(new_sample) 
   
    def stop(self):
        """ Stops streaming. """
        self.running = False
 
    def run(self):
        """ Loops for a specified time or forever. """
        current_sample = 0
        while current_sample < self.nsamp and self.running:
            if pylsl.local_clock()-self.last_push>=self.interval:
                self.last_push = pylsl.local_clock()
                current_sample+=1
                self.push_sample()
            #time.sleep(0.0001)
