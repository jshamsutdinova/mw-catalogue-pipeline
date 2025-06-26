from pathlib import Path
from ftplib import FTP
from datetime import date, timedelta


class Downloader:
    """
        Handles downloading of SRH correlation plots files from FTP server
    """
    FTP_HOST = "ftp.rao.istp.ac.ru"  # Adress from Observatory in Badary
    # FTP_HOST = "badary.iszf.irk.ru"  # Adress from external network
    FTP_USER = "anonymous"
    FTP_PASS = ""
    FTP_ROOT = "/SRH/corrPlot/"

    def __init__(self, local_base_dir):
        self.local_base_dir = local_base_dir

    def download_date_range(self, start_date, end_date):
        """ Download files from a range of dates. """
        with FTP(self.FTP_HOST, self.FTP_USER, self.FTP_PASS) as ftp:
            ftp.cwd(self.FTP_ROOT)

            for dt in self._daterange(start_date, end_date):
                self._download_files_for_date(ftp, dt)
        # ftp.quit()

    @staticmethod
    def _daterange(start_date, end_date):
        """ Return list of dates between time range. """
        days = int((end_date - start_date).days)+1
        for n in range(days):
            yield start_date + timedelta(n)

    @staticmethod
    def _generate_fnames(date):
        """ Get file name of corr. plots for three bands. """
        bands = ['0306', '0612', '1224']
        date_str = date.strftime(format='%Y%m%d')
        return [f'srh_{band}_cp_{date_str}.fits' for band in bands]

    def _download_files_for_date(self, ftp, date):
        """ Donwload files for three bands in one day. """
        year = date.year
        month = f'{date.month:02d}'
        remote_dir = f"{year}/{month}/"
        dir_to_save = Path(f'{self.local_base_dir}{year}/{month}/')
        dir_to_save.mkdir(parents=True, exist_ok=True)

        try:
            ftp.cwd(remote_dir)
            dir_to_save.mkdir(parents=True, exist_ok=True)

            for fname in self._generate_fnames(date):
                if fname in ftp.nlst():
                    self._download_file(ftp, fname, dir_to_save)
        except Exception as e:
            print(f'Error while accessing a directory {year}/{month}/: {e}')
        finally:
            ftp.cwd(self.FTP_ROOT)

    @staticmethod
    def _download_file(ftp, filename, dir_to_save):
        """ Download file from FTP server to local dir. """
        local_path = dir_to_save / filename
        with open(local_path, 'wb') as ff:
            ftp.retrbinary(f"RETR {filename}", ff.write)
        print(f"Downloaded: {filename}")


if __name__ == "__main__":
    start_dt = date(2025, 2, 11)
    end_dt = date(2025, 2, 13)

    downloader = Downloader('pipeline/data/corr_plots/')
    downloader.download_date_range(start_dt, end_dt)
