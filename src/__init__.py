import mobase
import re
from typing import List

class Plugin:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name

        # add exceptions here:
        self.dict = {
            # "mod1 regex": ["1st plugin substr", "substr in 2nd", "etc."] ,
            # "mod2 regex": ["substr in 1st", "substr in 2nd", "etc."]
        }

    def __lt__(self, other) -> bool:
        if self.priority != other.priority:
            return self.priority < other.priority

        lc_a = self.name.lower()
        lc_b = other.name.lower()
        for (k, arr) in self.dict.items():
            if re.search(k, lc_a):
                for n in arr:
                    if n in lc_a:
                        return True
                    if n in lc_b:
                        return False

        # within a plugin there can be several esps. something that fixes stuff
        # should come last. if not enough use self.dict for the exceptions

        patts = \
            ["(:?hot|bug)[ ._-]?fix",
                r"\bfix\b",
                "patch",
                "add[ ._-]?on",
                "expansion",
                "expanded",
                "extension",
                "ext",
                "remastered"]
        for pattern in patts:
            if re.search(pattern, lc_a) != re.search(pattern, lc_b):
                return re.search(pattern, lc_a) is None

        # generally shorter should come first
        return len(lc_a) < len(lc_b) or self.name < other.name

'''
class GamePluginsRequirement(mobase.IPluginRequirement):

    def __init__(self):
        super().__init__()

    def check(self, organizer: mobase.IOrganizer):
        managedGame = organizer.managedGame()
        if (managedGame and not managedGame.feature(mobase.GamePlugins)):
            return mobase.IPluginRequirement.Problem(
                "This plugin can only be enabled for games with plugins.")

        return None '''

class PluginSync(mobase.IPluginTool):

    _organizer: mobase.IOrganizer
    _modList: mobase.IModList
    _pluginList: mobase.IPluginList

    _isMo2Updated: bool

    def __init__(self):
        super().__init__()

    def init(self, organizer: mobase.IOrganizer):
        self._organizer = organizer
        self._modList = organizer.modList()
        self._pluginList = organizer.pluginList()

        version = self._organizer.appVersion().canonicalString()
        versionx = re.sub("[^0-9.]", "", version)
        self._version = float(".".join(versionx.split(".", 2)[:-1]))
        self._isMo2Updated = self._version >= 2.5

        return True

    # Basic info
    def name(self) -> str:
        return "Sync Plugins"

    def author(self) -> str:
        return "coldrifting"

    def description(self) -> str:
        return "Syncs plugin load order with mod order"

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(1, 2, 0, mobase.ReleaseType.FINAL)

    # Settings
    def isActive(self) -> str:
        return (self._organizer.managedGame().feature(mobase.GamePlugins))

    def settings(self) -> List[mobase.PluginSetting]:
        return [
            mobase.PluginSetting("enabled", "enable this plugin", True)
        ]

    # Display
    def displayName(self) -> str:
        return "Sync Plugins"

    def tooltip(self) -> str:
        return "Enables all Mods one at a time to match load order"

    def icon(self):
        if (self._isMo2Updated):
            from PyQt6.QtGui import QIcon
        else:
            from PyQt5.QtGui import QIcon

        return QIcon()

    # Plugin Logic
    def display(self) -> bool:
        # Get all plugins as a list
        allPlugins = self._pluginList.pluginNames()

        # Sort the list by plugin origin
        allPlugins = sorted(
            allPlugins,
            key=lambda
            x: Plugin(self._modList.priority(self._pluginList.origin(x)), x)
        )

        # Split into two lists, master files and regular plugins
        plugins = []
        masters = []
        for plugin in allPlugins:
            if (self._isMo2Updated):
                isMasterPlugin = self._pluginList.isMasterFlagged(plugin)
            else:
                isMasterPlugin = self._pluginList.isMaster(plugin)

            if (isMasterPlugin):
                masters.append(plugin)
            else:
                plugins.append(plugin)

        # Merge masters into the plugin list at the begining
        allPlugins = masters + plugins

        # Set load order
        self._pluginList.setLoadOrder(allPlugins)

        # Update the plugin list to use the new load order
        self._organizer.managedGame().feature(
            mobase.GamePlugins).writePluginLists(self._pluginList)

        # Refresh the UI
        self._organizer.refresh()

        return True


# Tell Mod Organizer to initialize the plugin
def createPlugin() -> mobase.IPlugin:
    return PluginSync()
