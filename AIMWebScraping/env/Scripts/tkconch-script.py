#!"C:\Users\avand\Documents\Visual Studio 2017\Projects\AIMWebScraping\AIMWebScraping\env\Scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'Twisted==19.2.0','console_scripts','tkconch'
__requires__ = 'Twisted==19.2.0'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('Twisted==19.2.0', 'console_scripts', 'tkconch')()
    )