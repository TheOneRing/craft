from Package.CMakePackageBase import *
import info
import shutil
import os
import re
import urllib.request, urllib.parse, urllib.error
import emergePlatform

class subinfo(info.infoclass):
    def setTargets( self ):
        if emergePlatform.buildArchitecture() == 'x64':
            self.targets[ '20100330' ] =  'http://downloads.sourceforge.net/project/virtuoso/virtuoso/6.1.1/vos6-win64-20100330.zip'
            self.targets['6.1.6'] = \
                "http://downloads.sourceforge.net/project/virtuoso/virtuoso/6.1.6/virtuoso-opensource-win64-20120802.zip"
        else:
            self.targets['6.1.6'] = \
                "http://downloads.sourceforge.net/project/virtuoso/virtuoso/6.1.6/virtuoso-opensource-win32-20120802.zip"
            self.targets[ '20100330' ] = \
                'http://downloads.sourceforge.net/project/virtuoso/virtuoso/6.1.1/vos6-win32-20100330.zip'
            self.targetDigests['20100330'] = 'f93f7606a636beefa4c669e8fc5d0100217d85c4'
            self.targetDigests['6.1.6'] = '7542bf14ec40517813a0d293c9e9023b1b305e62'
        self.targetInstSrc[ '20100330' ] = "virtuoso-opensource"
        self.targetInstSrc[ '6.1.6' ] = "virtuoso-opensource"
        self.shortDescription = "a middleware and database engine hybrid for RDBMS, ORDBMS, virtual database, RDF, XML, free-text, web application server and file server functionality"
        self.defaultTarget = '6.1.6'

    def setDependencies( self ):
        self.buildDependencies['virtual/bin-base'] = 'default'

class Package(CMakePackageBase):
  def __init__(self):
    self.subinfo = subinfo()
    self.subinfo.options.package.packSources = False
    self.subinfo.options.package.withCompiler = None
    CMakePackageBase.__init__( self )


  def compile( self ):
    return True

  def install( self ):
    if( not self.cleanImage()):
      return False

    shutil.copytree( self.sourceDir() , self.installDir(),ignore=shutil.ignore_patterns('libexpat.dll' ))

    return True

if __name__ == '__main__':
    Package().execute()
