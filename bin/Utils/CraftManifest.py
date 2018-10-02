import collections
import datetime
import json
import os


from CraftCore import CraftCore
import utils

from CraftBase import CraftBase
from options import UserOptions


class CraftManifestEntryFile(object):
    def __init__(self, fileName : str, checksum : str, version : str="", package : CraftBase=None) -> None:
        self.fileName = fileName
        self.checksum = checksum
        self.date = datetime.datetime.utcnow()
        self.version = version
        self.buildPrefix = CraftCore.standardDirs.craftRoot()
        self.options = {}

        if package:
            self.version = package.version
            settings = UserOptions.instance().settings
            self.options = dict(settings[package.package.path]) if settings.has_section(package.package.path) else {}

    @staticmethod
    def fromJson(data : dict):
        out = CraftManifestEntryFile(data["fileName"], data["checksum"])
        out.date = CraftManifest._parseTimeStamp(data["date"])
        out.version = data.get("version", "")
        out.buildPrefix = data.get("buildPrefix", None)
        out.options = data.get("options", {})
        return out

    def toJson(self) -> dict:
        return {"fileName"      : self.fileName,
                "checksum"      : self.checksum,
                "date"          : self.date.strftime(CraftManifest._TIME_FORMAT),
                "version"       : self.version,
                "buildPrefix"   : self.buildPrefix,
                "options"       : self.options}

class CraftManifestEntry(object):
    def __init__(self, name : str) -> None:
        self.name = name
        self.files = []

    @staticmethod
    def fromJson(data : dict):
        entry = CraftManifestEntry(data["name"])
        entry.files = sorted([CraftManifestEntryFile.fromJson(fileData) for fileData in data["files"]], key=lambda x:x.date, reverse=True)
        return entry

    def toJson(self) -> dict:
        return {"name":self.name, "files":[x.toJson() for x in self.files]}

    def addFile(self, fileName : str, checksum : str, version : str="", package : CraftBase=None) -> CraftManifestEntryFile:
        f = CraftManifestEntryFile(fileName, checksum, version, package)
        self.files.insert(0, f)
        return f

    @property
    def latest(self) -> CraftManifestEntryFile:
        return self.files[0] if self.files else None

class CraftManifest(object):
    _TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self):
        self.date = datetime.datetime.utcnow()
        self.packages = {str(CraftCore.compiler) : {}}
        self.origin = None

    @staticmethod
    def version() -> int:
        return 1

    @staticmethod
    def _migrate0(data : dict):
        manifest = CraftManifest()
        packages = manifest.packages[str(CraftCore.compiler)]
        for name, package in data.items():
            if not name in packages:
                packages[name] = CraftManifestEntry(name)
            p = packages[name]
            for fileName, pData in data[name].items():
                f = p.addFile(fileName, pData["checksum"])
                f.date = datetime.datetime(1, 1, 1)
        return manifest

    @staticmethod
    def fromJson(data : dict):
        version = data.get("version", 0)
        if version == 0:
            return CraftManifest._migrate0(data)
        elif version != CraftManifest.version():
            raise Exception("Invalid manifest version detected")

        manifest = CraftManifest()
        manifest.date = CraftManifest._parseTimeStamp(data["date"])
        manifest.origin = data.get("origin", None)
        for compiler in data["packages"]:
            manifest.packages[compiler] = {}
            for package in data["packages"][compiler]:
                p = CraftManifestEntry.fromJson(package)
                manifest.packages[compiler][p.name] = p
        return manifest

    def update(self, other):
        for compiler in other.packages.keys():
            if not compiler in self.packages:
                self.packages[compiler] = {}
            self.packages[compiler].update(other.packages[compiler])

    def toJson(self) -> dict:
        out = {"date": str(self.date), "origin": self.origin, "packages":{}, "version": CraftManifest.version()}
        for compiler, packages in self.packages.items():
            out["packages"][compiler] = [x.toJson() for x in self.packages[compiler].values()]
        return out

    def get(self, package : str) -> CraftManifestEntry:
        compiler = str(CraftCore.compiler)
        if not compiler in self.packages:
            self.packages[compiler] = {}
        if not package in self.packages[compiler]:
            self.packages[compiler][package] = CraftManifestEntry(package)
        return self.packages[compiler][package]

    def dump(self, cacheFilePath, includeTime=False):
        if includeTime:
            name, ext = os.path.splitext(cacheFilePath)
            cacheFilePath = f"{name}-{self.date.strftime('%Y%m%dT%H%M%S')}{ext}"
        self.date = datetime.datetime.utcnow()
        with open(cacheFilePath, "wt+") as cacheFile:
            json.dump(self, cacheFile, sort_keys=True, indent=2, default=lambda x:x.toJson())

    @staticmethod
    def load(manifestFileName : str, urls : [str]=None):
        """
        Load a manifest.
        If a url is provided a manifest is fetch from that the url and merged with a local manifest.
        TODO: in that case we are merging all repositories so we should also merge the cache files
        """
        old = None
        if not urls and ("ContinuousIntegration", "RepositoryUrl") in CraftCore.settings:
            urls = [CraftCore.settings.get("ContinuousIntegration", "RepositoryUrl").rstrip("/")]
        if urls:
            old = CraftManifest()
            for url in urls:
                new = CraftManifest.fromJson(CraftCore.cache.cacheJsonFromUrl(f"{url}/manifest.json"))
                if new:
                    new.origin = url
                    new.dump(manifestFileName, includeTime=True)
                    old.update(new)

        cache = None
        if os.path.isfile(manifestFileName):
            try:
                with open(manifestFileName, "rt+") as cacheFile:
                    cache = CraftManifest.fromJson(json.load(cacheFile))
                cache.dump(manifestFileName, includeTime=True)
            except Exception as e:
                CraftCore.log.warning(f"Failed to load {cacheFile}, {e}")
                pass
        if old:
            if cache:
                old.update(cache)
            return old
        if not cache:
            return CraftManifest()
        return cache

    @staticmethod
    def _parseTimeStamp(time : str) -> datetime.datetime:
        return datetime.datetime.strptime(time, CraftManifest._TIME_FORMAT)
