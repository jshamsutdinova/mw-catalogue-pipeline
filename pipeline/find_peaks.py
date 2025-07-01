import numpy as np
from pathlib import Path
from datetime import date
from astropy.io import fits
from flux_processing import FluxProcessing


class FindPeak:
    """ This class based on algorithm to find peaks in correlations plots """

    def __init__(self):
        self.basedir = 'pipeline/data/corr_plots'
        self.std = np.load('pipeline/data/std/std_20230713.npy')
        self.flux_process_obj = None

        self.num_events = []
        self.flare_duration = []
        self.flare_max = []
        self.flare_start = []
        self.flare_end = []
        self.freq = []

    def process_data(self, date):
        """ Process with corr.plots in three frequency bands to find peaks. """
        fnames = self._generate_fnames(date)
        tm_ref = self._initialize_time_reference(fnames[0])
        self.flux_process_obj = FluxProcessing(tm_ref)
        
        for fname in fnames:
            freq, time, flux = self._read_fits(fname)

    def _initialize_time_reference(self, fname):
        """ Set the common time reference grid from the first file. """
        with fits.open(f'{self.basedir}/{fname}') as hdul:
            tm_ref = hdul[2].data['time'][0]
        return tm_ref

    def _read_fits(self, fname):
        """ Read FITS file of SRH. """
        fpath = Path(f'{self.basedir}/{fname}')
        if not fpath.is_file():
            raise FileNotFoundError(f"SRH file not found: {fpath}")

        with fits.open(fpath) as hdul:
            freq = hdul[1].data['frequencies']
            time = hdul[2].data['time']
            flux = hdul[2].data['I']
                        
            for idx in range(freq.shape[0]):
                proccessed_flux = self.flux_process_obj.process_flux(flux[idx], time[idx])
                peaks = self._find_peaks()

        return freq, time, flux

    @staticmethod
    def _generate_fnames(date):
        """ Get file name of corr. plots for three bands. """
        bands = ['0306', '0612', '1224']
        date_str = date.strftime(format='%Y%m%d')
        year = date.year
        month = f'{date.month:02d}'
        return [f'{year}/{month}/srh_{band}_cp_{date_str}.fits' for band in bands]

    def _process_flux(self):
        """ Process a frequency channel's flux data. """
        # interpolate
        # remove outliers
        # remove trend and smooth
        pass

    def _interpolate(self):
        """ Interpolate flux to the common time reference grid. """
        pass

    def _remove_outliers_z_score(self):
        """ Apply Z-scores to remove instrumental outliers. """
        pass

    def _remove_trend(self):
        """ Remove the slow-varying trend from flux values. """

    def _find_peaks(self):
        """ Find peaks in flux (corr.plots). """
        pass


if __name__ == "__main__":
    peaks = FindPeak()
    dt = date(2025, 1, 3)

    peaks.process_data(dt)
