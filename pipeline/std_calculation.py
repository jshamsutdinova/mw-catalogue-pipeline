import os
import glob
from astropy.io import fits
import numpy as np


class StdCalculation:
    """
        This class calculate std for one day on the three SRH arrays.
        These values are reference
    """

    def __init__(self):
        self.fdir = 'pipeline/data/std'
        self.fnames = sorted(glob.glob(os.path.join(self.fdir, "*.fits")))
        self.tm_ref = None

    def process_srh_data(self):
        """ Read SRH fits file. Return std for every frequency (???) """
        # Initialize time reference from first file
        with fits.open(self.fnames[0]) as hdul:
            self.tm_ref = hdul[2].data['time'][0]

        std = np.array([])

        for fname in self.fnames:
            with fits.open(fname) as hdul:
                freq = hdul[1].data['frequencies']
                time = hdul[2].data['time']
                flux = hdul[2].data['I']

                # Process each frequentcy channel
                fluxes_intrp = []

                for i in range(freq.shape[0]):
                    flux_intrp = self.interpolate(time[i], flux[i])

        return time

    def interpolate(self, time, flux):
        """ Do interpolation of time profile (flux) to common time grid """
        flux_grid = np.reshape(flux, time.shape[0])
        flux_intrp = np.interp(self.tm_ref, time, flux_grid)

        return flux_intrp

    def preprocess_flux(self):
        pass

    def find_std(self):
        pass


if __name__ == '__main__':
    std = StdCalculation()
    std.process_srh_data()
