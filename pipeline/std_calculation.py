import os
import glob
import numpy as np
import scipy.ndimage
from astropy.io import fits
from scipy.signal import savgol_filter


class StdCalculation:
    """
        Calculates standard deviation values for Siberian Radioheliograph (SRH) data
        across three arrays for a given day.

        This class processes FITS files containing SRH correlation plots
    """

    def __init__(self):
        self.fdir = 'pipeline/data/std'
        self.fpaths = self._load_file_path()
        self.tm_ref = None

    def _load_file_path(self):
        """ Load and sort FITS file paths from the data directory."""
        paths = sorted(glob.glob(os.path.join(self.fdir, "*.fits")))
        if not paths:
            raise FileNotFoundError(f'No FITS files found in {self.fdir}')
        return paths

    def calculate_std_deviations(self):
        """
        Calculate std deviations values for all frequency.

        Returns:
            numpy.ndarray: Array std deviation values with shape (3, 16)
                           representing the three SRH arrays and 16 frequency
                           channels.
        """
        self._initialize_time_reference()

        std_result = np.zeros((3, 16))  # 3 arrays, 16 frequencies

        for idx, fpath in enumerate(self.fpaths):
            std_result[idx] = self._process_srh_data(fpath)

        return std_result

    def _initialize_time_reference(self):
        """ Set the common time reference grid from the first file. """
        with fits.open(self.fpaths[0]) as hdul:
            self.tm_ref = hdul[2].data['time'][0]

    def _process_srh_data(self, fpath):
        """
        Process a SRH fits file and calculate std deviations.

        Args:
            fpath (str): Path to SRH FITS file

        Returns:
            numpy.ndarray: std deviation values for all frequency channels
        """
        with fits.open(fpath) as hdul:
            freq = hdul[1].data['frequencies']
            time = hdul[2].data['time']
            flux = hdul[2].data['I']

            std_values = np.zeros(freq.shape[0])

            for i in range(freq.shape[0]):
                proccessed_flux = self._process_flux(time[i], flux[i])
                std_values[i] = self._calculate_flux_std(proccessed_flux)

        return std_values

    def _process_flux(self, time, flux):
        """
        Process a frequency channel's flux data.

        Args:
            time (numpy.ndarray): Time points for the channel
            flux (numpy.ndarray): Flux values for the channel

        Returns:
            numpy.ndarray: Processed flux values ready for std calculation
        """
        # Interpolate to common time grid
        interpolated = self._interpolate(time, flux)

        # Remove outliers
        cleaned = self._remove_outliers_z_score(interpolated[:10193])

        # Remove trend amd smooth
        detrended = self._remove_trend(cleaned)
        smoothed = savgol_filter(detrended, window_length=3, polyorder=2)

        return smoothed

    def _calculate_flux_std(self, flux):
        """ Calculate the standard deviation of processed flux values. """
        flux_diff = np.diff(flux)
        smooth_diff = savgol_filter(flux_diff, window_length=68, polyorder=2)
        return 3 * np.std(smooth_diff[9000:9500])

    def _interpolate(self, time, flux):
        """ Interpolate flux to the common time reference grid. """
        flux_grid = np.reshape(flux, time.shape[0])
        flux_intrp = np.interp(self.tm_ref, time, flux_grid)

        return flux_intrp

    def _remove_trend(self, flux):
        """ Remove the slow-varying trend from flux values. """
        flux_norm = flux / np.max(flux)
        flux_trend = flux_norm - scipy.ndimage.median_filter(flux_norm, size=1000)

        return flux_trend

    def _remove_outliers_z_score(self, flux, threshold=3.0):
        """ Apply Z-scores to remove instrumental outliers """
        z_scores = (flux - np.mean(flux)) / np.std(flux)
        flux_new = flux[abs(z_scores) <= threshold]

        return flux_new


if __name__ == '__main__':
    obj = StdCalculation()
    std = obj.calculate_std_deviations()
    
    np.save('pipeline/data/std/std_20230713.npy', std)
