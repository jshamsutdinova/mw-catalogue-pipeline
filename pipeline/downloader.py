from pathlib import Path
from ftplib import FTP
from datetime import date, timedelta


class Downloader:
    """ 
        Handles downloading of SRH correlation plots files from FTP server 
    """
    HOSTNAME = "badary.iszf.irk.ru"
    USERNAME = "anonymous"
    PASSWORD = ""

    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.date_range = self._daterange()
           
    def _load_file_ftp(self):
        """ Load the FITS files for three arrays from the FTP server """
        
        ftp = FTP(self.HOSTNAME, self.USERNAME, self.PASSWORD)
        ftp.cwd('/SRH/corrPlot/')

        for dt in self.date_range:
            year = dt.year
            month = '{:02d}'.format(dt.month)
            dir_to_save = Path(f'pipeline/data/corr_plots/{year}/{month}/')
            dir_to_save.mkdir(parents=True, exist_ok=True)
            try:
                ftp.cwd(f'{year}/{month}/')
                fnames = self._generate_fnames(dt)

                for fname in fnames:                
                    if fname in ftp.nlst():
                        with open(dir_to_save/fname, 'wb') as ff:
                            ftp.retrbinary(f'RETR {fname}', ff.write)
                            print(f'{fname} is downloaded')
            except Exception as e:
                print(f'Error while accessing a directory {year}/{month}/: {e}')
            finally:
                ftp.cwd('/SRH/corrPlot/')

        ftp.quit()
        

    def _daterange(self):
        """ Return list of dates between time range """
        days = int((self.end_date - self.start_date).days)+1
        for n in range(days):
            yield self.start_date + timedelta(n)
    
    @staticmethod
    def _generate_fnames(date):
        """ Get file name of corr. plots for three bands """
        bands = ['0306', '0612', '1224']
        date_str = date.strftime(format='%Y%m%d')
        return [f'srh_{band}_cp_{date_str}.fits' for band in bands]


if __name__ == "__main__":
    start_dt = date(2025, 1, 1)
    end_dt = date(2025, 1, 3)
    
    flares = Downloader(start_dt, end_dt)
    flares._load_file_ftp()
