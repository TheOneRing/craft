import base
import os
import sys
import info

class subinfo(info.infoclass):
    def setTargets( self ):
        self.svnTargets['svnHEAD'] = '[git]kde:kmplot|KDE/4.7|'
        for ver in ['0', '1', '2', '3', '4']:
            self.targets['4.7.' + ver] = "ftp://ftp.kde.org/pub/kde/stable/4.7." + ver + "/src/kmplot-4.7." + ver + ".tar.bz2"
            self.targetInstSrc['4.7.' + ver] = 'kmplot-4.7.' + ver
        self.targetDigests['4.7.0'] = '5123c7855497e6374dbd7211890cf9e69a4ee886'
        self.patchToApply['4.7.0'] = ("kmplot-4.7.0-20110819.diff", 1)
        self.shortDescription = 'mathematical function plotter'
        self.defaultTarget = 'svnHEAD'

    def setDependencies( self ):
        self.dependencies['kde/kde-runtime'] = 'default'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = "-DBUILD_doc=OFF"

if __name__ == '__main__':
    Package().execute()
