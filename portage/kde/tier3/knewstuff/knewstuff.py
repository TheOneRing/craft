import info


class subinfo(info.infoclass):
    def setTargets( self ):
        self.versionInfo.setDefaultValues( )

        self.shortDescription = "Support for downloading application assets from the network"


    def setDependencies( self ):
        self.buildDependencies["virtual/base"] = "default"
        self.buildDependencies["dev-util/extra-cmake-modules"] = "default"
        self.dependencies["libs/qtbase"] = "default"
        self.dependencies["frameworks/karchive"] = "default"
        self.dependencies["kde/kcompletion"] = "default"
        self.dependencies["frameworks/kconfig"] = "default"
        self.dependencies["frameworks/kcoreaddons"] = "default"
        self.dependencies["frameworks/ki18n"] = "default"
        self.dependencies["kde/kiconthemes"] = "default"
        self.dependencies["kde/kio"] = "default"
        self.dependencies["frameworks/kitemviews"] = "default"
        self.dependencies["kde/ktextwidgets"] = "default"
        self.dependencies["frameworks/kwidgetsaddons"] = "default"
        self.dependencies["kde/kxmlgui"] = "default"

from Package.CMakePackageBase import *

class Package(CMakePackageBase):
    def __init__( self ):
        CMakePackageBase.__init__( self )
