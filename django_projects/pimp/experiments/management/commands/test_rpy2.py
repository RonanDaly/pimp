from django.core.management.base import BaseCommand

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

class Command(BaseCommand):
    help = 'Test the rpy2 connection'

    def handle(self, *args, **options):
        
        print '******************************************'
        print 'Test rpy2 connection'
        print '******************************************'
        
        packrat_lib_path = '/Users/joewandy/git/pimp/packrat/lib/x86_64-apple-darwin15.5.0/3.3.1/'
        set_lib_path = robjects.r['.libPaths']
        set_lib_path(packrat_lib_path)

        importr('PiMP')    
        base = importr('base')
        base.options('java.parameters=paste("-Xmx",1024*8,"m",sep=""')