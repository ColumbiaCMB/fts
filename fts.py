import numpy as np
import scipy.fftpack
from matplotlib import pyplot as plt

class FTSData(object):
    def __init__(self,filename=None,white_light_fringe_offset='auto',max_offset=None):
        if filename is not None:
            self.load_from_file(filename)
            self.analyze(white_light_fringe_offset=white_light_fringe_offset,max_offset=max_offset)
    def load_from_file(self,filename):
        fh = open(filename,'r')
        lines = fh.readlines()
        fh.close()
        self.info = {}
        data = []
        for line in lines:
            if line.find(':') >=0:
                line = line.strip()
                k,v = line.split(':')
                self.info[k.strip()] = v.strip()
            elif line[0] == '\n':
                continue
            else:
                parts = line.split()
                x = float(parts[0])
                y = float(parts[1])
                data.append((x,y))
        if 'Note' in self.info:
            self.title = self.info['Note']

        self.raw_data = np.array(data)
        self.raw_position = self.raw_data[:,0]
        self.raw_visibility = self.raw_data[:,1]
    def load_from_npz(self,filename):
        fh = np.load(filename)
        x = fh['position']/20000.0 # convert counts to cm
        y = fh['r']
        self.raw_data = np.vstack((x,y)).T
        self.raw_position = x
        self.raw_visibility = y
        self.title = filename
    def analyze(self,white_light_fringe_offset,detrend=plt.mlab.detrend_linear,max_offset = None,window=np.hanning):
        if white_light_fringe_offset == 'auto':
            white_light_fringe_index = self.raw_visibility.argmax()
        else:
            white_light_fringe_index = np.abs(self.raw_position - white_light_fringe_offset).argmin()
        self.valid_position = self.raw_position[white_light_fringe_index:] - self.raw_position[white_light_fringe_index]
        self.valid_visibility = self.raw_visibility[white_light_fringe_index:]
        if max_offset is not None:
            max_index = np.abs(self.valid_position-max_offset).argmin()
            self.valid_position = self.valid_position[:max_index]
            self.valid_visibility = self.valid_visibility[:max_index]
        detrended = detrend(self.valid_visibility)
        trend = self.valid_visibility-detrended
        self.valid_visibility = detrended
        self.negative_visibility = self.raw_visibility[:white_light_fringe_index]
        self.negative_visibility = self.negative_visibility - trend[:len(self.negative_visibility)]
        self.negative_position = self.raw_position[white_light_fringe_index]-self.raw_position[:white_light_fringe_index]
        xmax = self.valid_position.max()
        freq_step_hz = 3e10 / (xmax) /4.0
        self.freq_step = freq_step_hz / 1e9
        self.raw_spectrum = (np.abs(scipy.fftpack.dct(self.valid_visibility)))
        self.window = window(self.valid_visibility.shape[0]*2)
        self.window = self.window[self.window.shape[0]/2:self.window.shape[0]/2+self.valid_visibility.shape[0]]
        self.windowed_visibility = self.valid_visibility*self.window
        self.windowed_spectrum = (np.abs(scipy.fftpack.dct(self.windowed_visibility)))
        self.raw_frequency = np.arange(len(self.raw_spectrum)) * self.freq_step
    def plot_interferogram(self,plot_negative=False,ax=None,windowed=False):
        if ax is None:
            fig,ax = plt.subplots(1,1)
        if windowed:
            ax.plot(self.valid_position,self.windowed_visibility,label='windowed')
        else:
            ax.plot(self.valid_position,self.valid_visibility,label='not windowed')
        if plot_negative:
            ax.plot(self.negative_position,self.negative_visibility,'--k',label='negative region')
        ax.grid(True)
        ax.set_xlabel('Path length difference [cm]')
        ax.set_ylabel('Visibility amplitude')

    def plot_spectrum(self,ax=None,log=True,freqs_to_note=()):
        if ax is None:
            fig,ax = plt.subplots(1,1)
        y = self.windowed_spectrum**2
        if log:
            y = 10*np.log10(y)
        ax.plot(self.raw_frequency,y)
        ax.set_ylim(y[1:].min(),y.max())
        ax.set_xlabel('Frequency [GHz]')
        if log:
            ax.set_ylabel('Power [dB]')
        else:
            ax.set_ylabel('Power [arb]')
        ax.grid(True)
        for freq in freqs_to_note:
            index = np.abs(self.raw_frequency-freq).argmin()
            yval = y[index]
            meas_freq = self.raw_frequency[index]
            ax.annotate(('%.3f GHz\n%.1f dB' % (meas_freq,yval)),
                        xy = (meas_freq,yval),
                        textcoords='offset points',
                        xytext=(0,12),
                        arrowprops=dict(facecolor='black',arrowstyle='->'),
                        horizontalalignment='right',
                        verticalalignment='bottom',
                        )
    def plot_summary(self,figsize=(12,8),zoom_region=(100,200)):
        fig,axs = plt.subplots(2,2,figsize=figsize)
        fig.suptitle(self.title)
        self.plot_interferogram(ax=axs[0,0])
        self.plot_interferogram(ax=axs[0,0],windowed=True)
        self.plot_interferogram(ax=axs[1,0],plot_negative=True)
        axs[1,0].set_xlim(0,2)
        axs[0,0].legend(loc='lower right',prop=dict(size='small'))
        axs[0,0].set_title('Interferogram')
        axs[1,0].legend(loc='lower right',prop=dict(size='small'))
        self.plot_spectrum(ax=axs[0,1],log=True)
        self.plot_spectrum(ax=axs[1,1],log=True)
        axs[1,1].set_xlim(zoom_region)
        axs[0,1].set_title('Spectrum')
        return fig,axs

