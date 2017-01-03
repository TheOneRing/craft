# -*- coding: utf-8 -*-
"""@brief utilities
this file contains some helper functions for craft
"""

# copyright:
# Holger Schroeder <holger [AT] holgis [DOT] net>
# Patrick Spendrin <ps_ml [AT] gmx [DOT] de>
# Ralf Habacker <ralf.habacker [AT] freenet [DOT] de>

import configparser
import time
import ftplib
import http.client
import inspect
import pickle
import shutil
import tarfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from operator import itemgetter
import atexit

from CraftDebug import craftDebug
import CraftHash
import Notifier.NotificationLoader
from CraftConfig import *
from CraftOS.osutils import OsUtils

# TODO: Rename
class UtilsCache(object):
    _instance = None
    _version = 0
    _cacheLifetime = (60 * 60 * 24) * 1  # days

    def __init__(self):
        self.version = UtilsCache._version
        self._appCache = {}
        self._helpCache = {}
        self._nightlyVersions = {}
        self.cacheCreationTime = time.time()

    @staticmethod
    def instance():
        if not UtilsCache._instance:
            UtilsCache._instance = UtilsCache()
            if os.path.exists(UtilsCache._cacheFile()):
                with open(UtilsCache._cacheFile(), "rb") as f:
                    try:
                        data = pickle.load(f)
                    except:
                        craftDebug.log.warning("Cache corrupted")
                        return UtilsCache._instance

                if data.version != UtilsCache._version or (time.time() - data.cacheCreationTime) > UtilsCache._cacheLifetime:
                    craftDebug.log.debug("Clear cache")
                else:
                    UtilsCache._instance = data
        return UtilsCache._instance

    @staticmethod
    def _cacheFile():
        return os.path.join(CraftStandardDirs.etcDir(), "cache.pickle")

    @staticmethod
    @atexit.register
    def _save():
        try:
            with open(UtilsCache._cacheFile(), "wb") as f:
                pickle.dump(UtilsCache.instance(), f)
        except:
            craftDebug.log.debug("Failed to save cache")
            deleteFile(UtilsCache._cacheFile())


    def findApplication(self, app) -> str:
        if app in self._appCache:
            return self._appCache[app]

        appLocation = shutil.which(app)
        if not appLocation:
            possibleAppLocation = os.path.join(CraftStandardDirs.craftBin(), "data", "binary", OsUtils.name(), app)
            extentions = [""]
            if OsUtils.isWin():
                extentions += [".exe", ".bat"]
            for ext in extentions:
                if os.path.exists(possibleAppLocation + ext):
                    appLocation = possibleAppLocation + ext
                    break
        else:
            #don't cache internal copies
            craftDebug.log.debug("Adding %s to app cache" % appLocation)
            self._appCache[app] = appLocation
        if not appLocation:
            craftDebug.log.debug("Craft was unable to locate: %s" % app)
            return None
        return appLocation

    # TODO: rename, cleanup
    def appSupportsCommand(self, app, command, helpCommand = "-h") -> str:
        if not (app, command) in self._helpCache:
            craftDebug.log.debug("%s %s" % (app, helpCommand))
            output = subprocess.getoutput("%s %s" %(app, helpCommand))
            supports = output.find( command ) != -1
            self._helpCache[(app, command)] = supports
            craftDebug.log.debug(output)
            craftDebug.log.debug("%s %s %s" % (app, "supports" if supports else "does not support", command))
        return self._helpCache[(app, command)]

    def getNightlyVersionsFromUrl(self, url, pattern, timeout = 10) -> [str]:
        """
        Returns a list of possible version number matching the regular expression in pattern.
        :param url: The url to look for the nightly builds.
        :param pattern: A regular expression to match the version.
        :param timeout:
        :return: A list of matching strings or [None]
        """
        if url not in self._nightlyVersions:
            if craftSettings.getboolean("General", "WorkOffline"):
                craftDebug.step("Nightly builds unavailable for %s in offline mode." % url)
                return []
            try:
                with urllib.request.urlopen(url, timeout = timeout) as fh:
                    data = str(fh.read(), "UTF-8")
                    vers = re.findall( pattern , data)
                    if not vers:
                        print(data)
                        raise Exception("Pattern %s does not match." % pattern)
                    self._nightlyVersions[url] = list(set(vers))
                    return self._nightlyVersions[url]
            except Exception as e:
                craftDebug.log.warning("Nightly builds unavailable for %s: %s" % (url, e))
        return self._nightlyVersions.get(url, [])

utilsCache = UtilsCache.instance()

def abstract():
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    raise NotImplementedError(caller + ' must be implemented in subclass')

def getCallerFilename():
    """ returns the file name of the """
    filename = None
    try:
        frame=inspect.currentframe()
        count = 2
        while count > 0 and frame:
            frame = frame.f_back
            # python 3.3 includes unnecessary importlib frames, skip them
            if frame and frame.f_code.co_filename != '<frozen importlib._bootstrap>':
                count -= 1
    finally:
        if frame:
            filename = frame.f_code.co_filename
            del frame
    return filename

### fetch functions

def getFiles( urls, destdir, suffix='' , filenames = ''):
    """download files from 'url' into 'destdir'"""
    craftDebug.log.debug("getfiles called. urls: %s, filenames: %s, suffix: %s" % (urls, filenames, suffix))
    # make sure distfiles dir exists
    if ( not os.path.exists( destdir ) ):
        os.makedirs( destdir )

    if type(urls) == list:
        urlList = urls
    else:
        urlList = urls.split()

    if filenames == '':
        filenames = [ os.path.basename(x) for x in urlList ]

    if type(filenames) == list:
        filenameList = filenames
    else:
        filenameList = filenames.split()

    dlist = list(zip( urlList , filenameList ))

    for url,filename in dlist:
        if ( not getFile( url + suffix, destdir , filename ) ):
            return False

    return True

def getFile( url, destdir , filename='' ) -> bool:
    """download file from 'url' into 'destdir'"""
    craftDebug.log.debug("getFile called. url: %s" % url)
    if url == "":
        craftDebug.log.error("fetch: no url given")
        return False

    if utilsCache.findApplication("wget"):
        return wgetFile( url, destdir , filename )


    if not filename:
        _, _, path, _, _, _ = urllib.parse.urlparse( url )
        filename = os.path.basename( path )

    if os.path.exists(os.path.join( destdir, filename )):
        return True

    width, _ =  shutil.get_terminal_size((80,20))

    def dlProgress(count, blockSize, totalSize):
        if totalSize != -1:
            percent = int(count * blockSize * 100 / totalSize)
            times = int((width - 20) / 100 * percent)
            sys.stdout.write(("\r%s%3d%%" % ("#" * times, percent)))
        else:
            sys.stdout.write(("\r%s bytes downloaded" % (count * blockSize)))
        sys.stdout.flush()

    urllib.request.urlretrieve(url, filename =  os.path.join( destdir, filename ), reporthook= dlProgress if craftDebug.verbose() >= 0 else None )

    if craftDebug.verbose()>=0:
        sys.stdout.write("\n")
        sys.stdout.flush()
    return True


def wgetFile( url, destdir, filename=''):
    """download file with wget from 'url' into 'destdir', if filename is given to the file specified"""
    command = "\"%s\" -c -t 10" % utilsCache.findApplication("wget")
    if craftSettings.getboolean("General", "EMERGE_NO_PASSIVE_FTP", False ):
        command += " --no-passive-ftp "
    if(filename ==''):
        command += "  -P \"%s\"" % destdir
    else:
        command += " -O \"%s\"" % os.path.join( destdir, filename )
    command += " %s" % url
    craftDebug.log.debug("wgetfile called")

    if craftDebug.verbose() < 1:
        command += " -q --show-progress"
        ret = system( command, displayProgress=True, stderr=subprocess.STDOUT)
    else:
        ret = system( command )
    craftDebug.log.debug("wget ret: %s" % ret)
    return ret

### unpack functions

def unpackFiles( downloaddir, filenames, workdir ):
    """unpack (multiple) files specified by 'filenames' from 'downloaddir' into 'workdir'"""

    for filename in filenames:
        if ( not unpackFile( downloaddir, filename, workdir ) ):
            return False

    return True

def unpackFile( downloaddir, filename, workdir ):
    """unpack file specified by 'filename' from 'downloaddir' into 'workdir'"""
    craftDebug.log.debug("unpacking this file: %s" % filename)

    ( shortname, ext ) = os.path.splitext( filename )
    if re.match( "(.*\.tar.*$|.*\.tgz$)", filename ):
        shutil.unpack_archive(os.path.join(downloaddir, filename),workdir)
        return True
    elif ext == "":
        return True
    return un7zip( os.path.join( downloaddir, filename ), workdir, ext )

def un7zip( fileName, destdir, flag = None ):
    command = utilsCache.findApplication("7za")
    command += " x -r -y -o\"%s\" \"%s\"" % ( destdir, fileName )

    if flag == ".7z":
        # Actually this is not needed for a normal archive.
        # But git is an exe file renamed to 7z and we need to specify the type.
        # Yes it is an ugly hack.
        command += " -t7z"
    if utilsCache.appSupportsCommand(utilsCache.findApplication("7za"), "-bs"):
        command += " -bso2"
        command += " -bsp1"
    return system( command , displayProgress=True)

def system(cmd, displayProgress=False, **kw ):
    """execute cmd in a shell. All keywords are passed to Popen. stdout and stderr
    might be changed depending on the chosen logging options."""
    kw['shell'] = True
    return systemWithoutShell(cmd, displayProgress, **kw)

def systemWithoutShell(cmd, displayProgress=False, **kw):
    """execute cmd. All keywords are passed to Popen. stdout and stderr
    might be changed depending on the chosen logging options.

    When the parameter "displayProgress" is True, stdout won't be
    logged to allow the display of progress bars."""

    craftDebug.log.debug("executing command: '%s' in '%s'" % (cmd, kw.get("cwd", os.getcwd())))
    if not displayProgress:
        stdout = kw.get('stdout', sys.stdout)
        if stdout == sys.stdout:
            kw["universal_newlines"] = True
        kw['stderr'] = subprocess.STDOUT
        kw['stdout'] = subprocess.PIPE
        proc = subprocess.Popen(cmd, **kw)
        for line in proc.stdout:
            if not stdout == sys.stdout:
                stdout.write(line)
                craftDebug.log.debug(line.rstrip())
            else:
                craftDebug.log.info(line.rstrip())
    else:
        kw['stderr'] = kw.get('stderr', subprocess.PIPE)
        kw["universal_newlines"] = True
        proc = subprocess.Popen(cmd, **kw)
        if proc.stderr:
            for line in proc.stderr:
                craftDebug.log.debug(line.rstrip())

    proc.communicate()
    return proc.wait() == 0

def getFileListFromDirectory( imagedir ):
    """ create a file list containing hashes """
    ret = []

    myimagedir = imagedir
    if ( not imagedir.endswith( "\\" ) ):
        myimagedir = myimagedir + "\\"

    algorithm = CraftHash.HashAlgorithm.SHA256
    for root, _, files in os.walk( imagedir ):
        for fileName in files:
            ret.append( ( os.path.join( root, fileName ).replace( myimagedir, "" ), algorithm.stringPrefix() + CraftHash.digestFile( os.path.join( root, fileName), algorithm) ) )
    return ret


def unmergeFileList(rootdir, fileList, forced=False):
    """ delete files in the fileList if has matches or forced is True """
    for filename, filehash in fileList:
        fullPath = os.path.join(rootdir, os.path.normcase( filename))
        if os.path.isfile(fullPath):
            algorithm = CraftHash.HashAlgorithm.getAlgorithmFromPrefix(filehash)
            if not algorithm:
                currentHash = CraftHash.digestFile(fullPath, CraftHash.HashAlgorithm.MD5)
            else:
                currentHash = algorithm.stringPrefix() + CraftHash.digestFile(fullPath, algorithm)
            if currentHash == filehash or filehash == "":
                OsUtils.rm(fullPath, True)
            else:
                if forced:
                    craftDebug.log.warning("file %s has different hash: %s %s, deleting anyway" % \
                            (fullPath, currentHash, filehash ))
                    OsUtils.rm(fullPath, True)
                else:
                    craftDebug.log.warning("file %s has different hash: %s %s, run with option --force to delete it anyway" % \
                            (fullPath, currentHash, filehash ))
        elif not os.path.isdir(fullPath):
            craftDebug.log.warning("file %s does not exist" % fullPath)

def mergeImageDirToRootDir( imagedir, rootdir , linkOnly = craftSettings.getboolean("General", "UseHardlinks", False )):
    copyDir( imagedir, rootdir , linkOnly)

def moveEntries( srcdir, destdir ):
    for entry in os.listdir( srcdir ):
        src = os.path.join( srcdir, entry )
        dest = os.path.join( destdir, entry )
        craftDebug.log.debug("move: %s -> %s" % (src, dest))
        if( os.path.isfile( dest ) ):
            os.remove( dest )
        if( os.path.isdir( dest ) ):
            continue
        os.rename( src, dest )

def cleanDirectory( directory ):
    craftDebug.log.debug("clean directory %s" % directory)
    if ( os.path.exists( directory ) ):
        for root, dirs, files in os.walk( directory, topdown=False):
            for name in files:
                if not OsUtils.rm(os.path.join(root, name), True):
                    craftDebug.log.critical("couldn't delete file %s\n ( %s )" % (name, os.path.join(root, name)))
            for name in dirs:
                if not OsUtils.rmDir(os.path.join(root, name), True):
                    craftDebug.log.critical("couldn't delete directory %s\n( %s )" % (name, os.path.join(root, name)))
    else:
        os.makedirs( directory )

def getVCSType( url ):
    """ return the type of the vcs url """
    if not url:
        return ""
    if isGitUrl( url ):
        return "git"
    elif url.find("://") == -1:
        return "svn"
    elif url.startswith("[hg]"):
        return "hg"
    elif url.find("svn:") >= 0 or url.find("https:") >= 0 or url.find("http:") >= 0:
        return "svn"
    ## \todo complete more cvs access schemes
    elif url.find("pserver:") >= 0:
        return "cvs"
    else:
        return ""

def isGitUrl( Url ):
    """ this function returns true, if the Url given as parameter is a git url:
        it either starts with git:// or the first part before the first '|' ends with .git
        or if the url starts with the token [git] """
    if Url.startswith('git://'):
        return True
    # split away branch and tags
    splitUrl = Url.split('|')
    if splitUrl[0].endswith(".git"):
        return True
    if Url.startswith("[git]"):
        return True
    return False

def splitVCSUrl( Url ):
    """ this function splits up an url provided by Url into the server name, the path, a branch or tag;
        it will return a list with 3 strings according to the following scheme:
        git://servername/path.git|4.5branch|v4.5.1 will result in ['git://servername:path.git', '4.5branch', 'v4.5.1']
        This also works for all other dvcs"""
    splitUrl = Url.split('|')
    if len(splitUrl) < 3:
        c = [x for x in splitUrl]
        for dummy in range(3 - len(splitUrl)):
            c.append('')
    else:
        c = splitUrl[0:3]
    return c

def replaceVCSUrl( Url ):
    """ this function should be used to replace the url of a server
        this comes in useful if you e.g. need to switch the server url for a push url on gitorious.org """
    configfile = os.path.join(CraftStandardDirs.etcPortageDir(), "..", "crafthosts.conf" )
    replacedict = dict()

    # FIXME handle svn/git usernames and settings with a distinct naming
    #todo WTF
    if ( ("General", "KDESVNUSERNAME") in craftSettings and
     craftSettings.get("General", "KDESVNUSERNAME") != "username" ) :
        replacedict[ "git://git.kde.org/" ] = "git@git.kde.org:"
    if os.path.exists( configfile ):
        config = configparser.ConfigParser()
        config.read( configfile )
        # add the default KDE stuff if the KDE username is set.
        for section in config.sections():
            host = config.get( section, "host" )
            replace = config.get( section, "replace" )
            replacedict[ host ] = replace

    for host in list(replacedict.keys()):
        if not Url.find( host ) == -1:
            Url = Url.replace( host, replacedict[ host ] )
            break
    return Url

def createImportLibs( dll_name, basepath ):
    """creating the import libraries for the other compiler(if ANSI-C libs)"""

    dst = os.path.join( basepath, "lib" )
    if( not os.path.exists( dst ) ):
        os.mkdir( dst )

    # check whether the required binary tools exist
    HAVE_GENDEF = utilsCache.findApplication("gendef") is not None
    USE_GENDEF = HAVE_GENDEF
    HAVE_LIB = utilsCache.findApplication("lib") is not None
    HAVE_DLLTOOL = utilsCache.findApplication("dlltool") is not None

    craftDebug.log.debug("gendef found:", HAVE_GENDEF)
    craftDebug.log.debug("gendef used:", USE_GENDEF)
    craftDebug.log.debug("lib found:", HAVE_LIB)
    craftDebug.log.debug("dlltool found:", HAVE_DLLTOOL)

    dllpath = os.path.join( basepath, "bin", "%s.dll" % dll_name )
    defpath = os.path.join( basepath, "lib", "%s.def" % dll_name )
    exppath = os.path.join( basepath, "lib", "%s.exp" % dll_name )
    imppath = os.path.join( basepath, "lib", "%s.lib" % dll_name )
    gccpath = os.path.join( basepath, "lib", "%s.dll.a" % dll_name )

    if not HAVE_GENDEF and os.path.exists( defpath ):
        HAVE_GENDEF = True
        USE_GENDEF = False
    if not HAVE_GENDEF:
        craftDebug.log.warning("system does not have gendef.exe")
        return False
    if not HAVE_LIB  and not os.path.isfile( imppath ):
        craftDebug.log.warning("system does not have lib.exe (from msvc)")
    if not HAVE_DLLTOOL and not os.path.isfile( gccpath ):
        craftDebug.log.warning("system does not have dlltool.exe")

    # create .def
    if USE_GENDEF:
        cmd = "gendef - %s -a > %s " % ( dllpath, defpath )
        system( cmd )

    if( HAVE_LIB and not os.path.isfile( imppath ) ):
        # create .lib
        cmd = "lib /machine:x86 /def:%s /out:%s" % ( defpath, imppath )
        system( cmd )

    if( HAVE_DLLTOOL and not os.path.isfile( gccpath ) ):
        # create .dll.a
        cmd = "dlltool -d %s -l %s -k" % ( defpath, gccpath )
        system( cmd )

    if os.path.exists( defpath ):
        os.remove( defpath )
    if os.path.exists( exppath ):
        os.remove( exppath )
    return True

def toMSysPath( path ):
    path = path.replace( '\\', '/' )
    if ( len(path) > 1 and path[1] == ':' ):
        path = '/' + path[0].lower() + '/' + path[3:]
    return path

def cleanPackageName( basename, packagename ):
    return os.path.basename( basename ).replace( packagename + "-", "" ).replace( ".py", "" )

def createDir(path):
    """Recursive directory creation function. Makes all intermediate-level directories needed to contain the leaf directory"""
    if not os.path.exists( path ):
        craftDebug.log.debug("creating directory %s " % (path))
        os.makedirs( path )
    return True

def copyFile(src, dest,linkOnly = craftSettings.getboolean("General", "UseHardlinks", False)):
    """ copy file from src to dest"""
    craftDebug.log.debug("copy file from %s to %s" % (src, dest))
    destDir = os.path.dirname( dest )
    if not os.path.exists( destDir ):
        os.makedirs( destDir )
    if os.path.exists( dest ):
        craftDebug.log.warning("Overriding %s" % dest)
        OsUtils.rm( dest, True )
    if linkOnly:
        try:
            os.link( src , dest )
            return True
        except:
            craftDebug.log.warning("Failed to create hardlink %s for %s" % (dest, src))
    shutil.copy(src,dest)
    return True

def copyDir( srcdir, destdir,linkOnly = craftSettings.getboolean("General", "UseHardlinks", False ) ):
    """ copy directory from srcdir to destdir """
    craftDebug.log.debug("copyDir called. srcdir: %s, destdir: %s" % (srcdir, destdir))

    if ( not srcdir.endswith( os.path.sep ) ):
        srcdir += os.path.sep
    if ( not destdir.endswith( os.path.sep ) ):
        destdir += os.path.sep

    for root, _, files in os.walk( srcdir ):
        # do not copy files under .svn directories, because they are write-protected
        # and the they cannot easily be deleted...
        if ( root.find( ".svn" ) == -1 ):
            tmpdir = root.replace( srcdir, destdir )
            if not os.path.exists( tmpdir ):
                os.makedirs( tmpdir )
            for fileName in files:
                copyFile(os.path.join( root, fileName ),os.path.join( tmpdir, fileName ), linkOnly)
                craftDebug.log.debug("copy %s to %s" % (os.path.join(root, fileName), os.path.join(tmpdir, fileName)))

    return True

def mergeTree(srcdir, destdir):
    """ copy directory from @p srcdir to @p destdir

    If a directory in @p destdir exists, just write into it
    """

    fileList = os.listdir(srcdir)
    for i in fileList:
        src = os.path.join(srcdir, i)
        dest = os.path.join(destdir, i)
        if os.path.exists(dest):
            if os.path.isdir(dest):
                mergeTree(src, dest)
                continue
            else:
                os.remove(dest)
        shutil.move(src, destdir)

    # Cleanup (only removing empty folders)
    os.rmdir(srcdir)

def moveDir( srcdir, destdir ):
    """ move directory from srcdir to destdir """
    craftDebug.log.debug("moveDir called. srcdir: %s, destdir: %s" % (srcdir, destdir))
    try:
        shutil.move( srcdir, destdir )
    except Exception as e:
        craftDebug.log.warning(e)
        return False
    return True

def rmtree( directory ):
    """ recursively delete directory """
    craftDebug.log.debug("rmtree called. directory: %s" % (directory))
    shutil.rmtree ( directory, True ) # ignore errors

def moveFile(src, dest):
    """move file from src to dest"""
    craftDebug.log.debug("move file from %s to %s" % (src, dest))
    shutil.move( src, dest )
    return True

def deleteFile(fileName):
    """delete file """
    if not os.path.exists( fileName ):
        return False
    craftDebug.log.debug("delete file %s " % (fileName))
    os.remove( fileName )
    return True

def findFiles( directory, pattern=None, fileNames=None):
    """find files recursivly"""
    if fileNames == None:
        fileNames = []
        pattern = pattern.lower()
    for entry in os.listdir(directory):
        if entry.find(".svn") > -1 or entry.find(".bak") > -1:
            continue
        fileName = os.path.join(directory, entry)
        if os.path.isdir(fileName):
            findFiles(fileName, pattern, fileNames)
        elif os.path.isfile(fileName) and pattern == None or entry.lower().find(pattern) > -1:
            fileNames.append(fileName)
    return fileNames

def putenv(name, value):
    """set environment variable"""
    craftDebug.log.debug("set environment variable -- set %s=%s" % (name, value))
    os.putenv( name, value )
    return True

def applyPatch(sourceDir, f, patchLevel='0'):
    """apply single patch"""
    cmd = 'patch -d "%s" -p%s -i "%s"' % (sourceDir, patchLevel, f)
    craftDebug.log.debug("applying %s" % cmd)
    result = system( cmd )
    if not result:
        craftDebug.log.warning("applying %s failed!" % f)
    return result

def getWinVer():
    '''
        Returns the Windows Version of the system returns "0" if the Version
        can not be determined
    '''
    try:
        result = str(subprocess.Popen("cmd /C ver", stdout=subprocess.PIPE).communicate()[0],"windows-1252")
    except OSError:
        craftDebug.log.debug("Windows Version can not be determined")
        return "0"
    version = re.search(r"\d+\.\d+\.\d+", result)
    if(version):
        return version.group(0)
    craftDebug.log.debug("Windows Version can not be determined")
    return "0"

def regQuery(key, value):
    '''
    Query the registry key <key> for value <value> and return
    the result.
    '''
    query = 'reg query "%s" /v "%s"' % (key, value)
    craftDebug.log.debug("Executing registry query %s " % query)
    result = subprocess.Popen(query,
                stdout = subprocess.PIPE).communicate()[0]
    # Output of this command is either an error to stderr
    # or the key with the value in the next line
    reValue = re.compile(r"(\s*%s\s*REG_\w+\s*)(.*)" % value)
    match = reValue.search(str(result, 'windows-1252'))
    if match and match.group(2):
        return match.group(2).rstrip()
    return False

def embedManifest(executable, manifest):
    '''
       Embed a manifest to an executable using either the free
       kdewin manifest if it exists in dev-utils/bin
       or the one provided by the Microsoft Platform SDK if it
       is installed'
    '''
    if not os.path.isfile(executable) or not os.path.isfile(manifest):
        # We die here because this is a problem with the portage files
        craftDebug.log.critical("embedManifest %s or %s do not exist" % (executable, manifest))
    craftDebug.log.debug("embedding ressource manifest %s into %s" % \
                     (manifest, executable))
    mtExe = None
    mtExe = os.path.join(CraftStandardDirs.craftRoot(), "dev-utils", "bin", "mt.exe")

    if(not os.path.isfile(mtExe)):
        # If there is no free manifest tool installed on the system
        # try to fallback on the manifest tool provided by visual studio
        sdkdir = regQuery("HKLM\SOFTWARE\Microsoft\Microsoft SDKs\Windows",
            "CurrentInstallFolder")
        if not sdkdir:
            craftDebug.log.debug("embedManifest could not find the Registry Key"
                             " for the Windows SDK")
        else:
            mtExe = r'%s' % os.path.join(sdkdir, "Bin", "mt.exe")
            if not os.path.isfile(os.path.normpath(mtExe)):
                craftDebug.log.debug("embedManifest could not find a mt.exe in\n\t %s" % \
                                 os.path.dirname(mtExe))
    if os.path.isfile(mtExe):
        return system([mtExe, "-nologo", "-manifest", manifest,
            "-outputresource:%s;1" % executable])
    else:
        return system(["mt", "-nologo", "-manifest", manifest,
            "-outputresource:%s;1" % executable])


def getscriptname():
    if __name__ == '__main__':
        return sys.argv[ 0 ]
    else:
        return __name__

def prependPath(*parts):
    """put path in front of the PATH environment variable, if it is not there yet.
    The last part must be a non empty string, otherwise we do nothing"""
    if parts[-1]:
        fullPath = os.path.join(*parts)
        old = os.getenv("PATH").split(';')
        if old[0] != fullPath:
            craftDebug.log.debug("adding %s to system path" % fullPath)
            old.insert(0, fullPath)
            putenv( "PATH", os.path.pathsep.join(old))

def notify(title,message,alertClass = None):
    craftDebug.step("%s: %s" % (title, message))
    backends = craftSettings.get( "General","EMERGE_USE_NOTIFY", "")
    if craftSettings.getboolean("ContinuousIntegration", "Enabled", False) or backends == "":
        return
    backends = Notifier.NotificationLoader.load(backends.split(";"))
    for backend in backends.values():
        backend.notify(title,message,alertClass)

def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s1:
        return len(s2)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


#taken from https://bitbucket.org/pypa/setuptools/src/a3d16c5f7443ec6e5e4d8d4791682b56130b41b5/pkg_resources.py?at=default


def parse_version(s):
    """Convert a version string to a chronologically-sortable key

    This is a rough cross between distutils' StrictVersion and LooseVersion;
    if you give it versions that would work with StrictVersion, then it behaves
    the same; otherwise it acts like a slightly-smarter LooseVersion. It is
    *possible* to create pathological version coding schemes that will fool
    this parser, but they should be very rare in practice.

    The returned value will be a tuple of strings.  Numeric portions of the
    version are padded to 8 digits so they will compare numerically, but
    without relying on how numbers compare relative to strings.  Dots are
    dropped, but dashes are retained.  Trailing zeros between alpha segments
    or dashes are suppressed, so that e.g. "2.4.0" is considered the same as
    "2.4". Alphanumeric parts are lower-cased.

    The algorithm assumes that strings like "-" and any alpha string that
    alphabetically follows "final"  represents a "patch level".  So, "2.4-1"
    is assumed to be a branch or patch of "2.4", and therefore "2.4.1" is
    considered newer than "2.4-1", which in turn is newer than "2.4".

    Strings like "a", "b", "c", "alpha", "beta", "candidate" and so on (that
    come before "final" alphabetically) are assumed to be pre-release versions,
    so that the version "2.4" is considered newer than "2.4a1".

    Finally, to handle miscellaneous cases, the strings "pre", "preview", and
    "rc" are treated as if they were "c", i.e. as though they were release
    candidates, and therefore are not as new as a version string that does not
    contain them, and "dev" is replaced with an '@' so that it sorts lower than
    than any other pre-release tag.
    """

    def _parse_version_parts(s):
        component_re = re.compile(r'(\d+ | [a-z]+ | \.| -)', re.VERBOSE)
        replace = {'pre':'c', 'preview':'c','-':'final-','rc':'c','dev':'@'}.get
        for part in component_re.split(s):
            part = replace(part,part)
            if not part or part=='.':
                continue
            if part[:1] in '0123456789':
                yield part.zfill(8)    # pad for numeric comparison
            else:
                yield '*'+part

        yield '*final'  # ensure that alpha/beta/candidate are before final

    parts = []
    for part in _parse_version_parts(s.lower()):
        if part.startswith('*'):
            if part<'*final':   # remove '-' before a prerelease tag
                while parts and parts[-1]=='*final-': parts.pop()
            # remove trailing zeros from each series of numeric parts
            while parts and parts[-1]=='00000000':
                parts.pop()
        parts.append(part)
    return tuple(parts)

def createBat(fileName, command):
    with open(fileName, "wt+") as bat:
        bat.write("@echo off\r\n")
        bat.write(command)
        bat.write("\r\n")
