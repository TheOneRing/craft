# -*- coding: utf-8 -*-
import info
import emergePlatform
import os

class subinfo(info.infoclass):
    def setDependencies( self ):
        self.buildDependencies['virtual/base'] = 'default'
        self.buildDependencies['win32libs-bin/automoc'] = 'default'
        self.dependencies['kdesupport/soprano'] = 'default'
        self.dependencies['win32libs-bin/boost-program-options']   = 'default'
        self.dependencies['win32libs-bin/libxslt'] = 'default'
        self.dependencies['libs/qt'] = 'default'
        self.dependencies['win32libs-bin/sqlite'] = 'default'
        self.dependencies['win32libs-bin/shared-mime-info'] = 'default'

    def setTargets( self ):
        baseurl = 'ftp://ftp.kde.org/pub/kde/stable/akonadi/src/akonadi-%s.tar.bz2'
        for ver in ['1.4.80', '1.4.90', '1.6.0','1.6.2', '1.7.90']:
            self.targets[ver] = baseurl % ver
            self.targetInstSrc[ver] = 'akonadi-' + ver

        self.svnTargets['gitHEAD'] = '[git]kde:akonadi.git'
        self.shortDescription = "a storage service for PIM data and meta data"
        self.defaultTarget = 'gitHEAD'

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        self.subinfo = subinfo()
        CMakePackageBase.__init__( self )
        self.subinfo.options.configure.defines = (
                " -DINSTALL_QSQLITE_IN_QT_PREFIX=TRUE"
                " -DDATABASE_BACKEND=SQLITE " )


if __name__ == '__main__':
    Package().execute()
