import numpy as np
import scipy.ndimage
from scipy.signal import savgol_filter


class FluxProcessing:
    """ This class processes with SRH flux data for subsequent analysis. """
    
    def __init__(self, tm_ref):
        self.tm_ref = tm_ref
    
    def _interpolate(self, time, flux):
        """ Interpolate flux to the common time reference grid. """
        flux_grid = np.reshape(flux, time.shape[0])
        flux_intrp = np.interp(self.tm_ref, time, flux_grid)

        return flux_intrp
    
    def cut_at_threshold(self, flux, cutoff):
        """ Cut arrays """
        cut_idx = np.searchsorted(self.tm_ref, cutoff, side='right')
        if cut_idx == len(self.tm_ref):
            return self.tm_ref, flux
        return self.tm_ref[:cut_idx], flux[:cut_idx]
    
    @staticmethod
    def _remove_outliers_z_score(time, flux, threshold=3.0):
        """ Apply Z-scores to remove instrumental outliers """
        print(flux)
        z_scores = (flux - np.mean(flux)) / np.std(flux)
        valid_mask = np.abs(z_scores) <= threshold

        cleaned_time = time[valid_mask]       
        cleaned_flux = flux[valid_mask]
        
        return cleaned_time, cleaned_flux
    
    def _fix_time_artefacts(time):
        """ Check monotonicaly increasing time values through linear interpolation. """
        pass

    @staticmethod
    def _remove_trend(flux):
        """ Remove the slow-varying trend from flux values. """
        flux_norm = flux / np.max(flux)
        flux_trend = flux_norm - scipy.ndimage.median_filter(flux_norm, size=1000)

        return flux_trend
    
    @staticmethod
    def _filter_positive_values(time, flux):
        """ Filters out non-positive values from flux and corresponding time points. """
        if len(flux) != len(time):
            raise ValueError("Flux and time arrays must have equal length")
        
        positive_mask = flux > 0
        return time[positive_mask], flux[positive_mask]

    def process_flux(self, flux, time):
        """ Method to process with data """
        # Interpolate to common time grid
        interpolated = self._interpolate(time, flux)
        tm_cutted, flux_cutted = self.cut_at_threshold(interpolated, 36000)
                
        # Remove outliers
        tm_cleaned, flux_cleaned = self._remove_outliers_z_score(tm_cutted, flux_cutted)
        
        # Remove trend amd smooth
        flux_detrended = self._remove_trend(flux_cleaned)
        
        tm_filtered, flux_filtered = self._filter_positive_values(tm_cleaned, flux_detrended)
        
        return tm_filtered, flux_filtered
        