from PyQt5.QtGui import QIcon

import mobase
import re


class Plugin:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name

        # add exceptions here:
        self.dict = {
            # "mod1 regex": ["1st plugin substr", "substr in 2nd", "etc."] ,
            # "mod2 regex": ["substr in 1st", "substr in 2nd", "etc."]
        }

    def __lt__(self, other):
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


class GamePluginsRequirement(mobase.IPluginRequirement):

    def __init__(self):
        super().__init__()

    def check(self, organizer: mobase.IOrganizer):
        managedGame = organizer.managedGame()
        if (managedGame and not managedGame.feature(mobase.GamePlugins)):
            return mobase.IPluginRequirement.Problem(
                "This plugin can only be enabled for games with plugins.")

        return None


class PluginSync(mobase.IPluginTool):

    _organizer: mobase.IOrganizer
    _modList: mobase.IModList
    _pluginList: mobase.IPluginList

    def __init__(self):
        super().__init__()

    def init(self, organizer: mobase.IOrganizer):
        self._organizer = organizer
        self._modList = organizer.modList()
        self._pluginList = organizer.pluginList()
        return True

    def name(self):
        return "Sync Plugins"

    def author(self):
        return "coldrifting"

    def description(self):
        return "Syncs plugin load order with mod order"

    def version(self):
        return mobase.VersionInfo(1, 0, 0, mobase.ReleaseType.FINAL)

    def isActive(self):
        return (self._organizer.managedGame().feature(mobase.GamePlugins))

    def settings(self):
        return []

    def display(self):
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
            if (self._pluginList.isMaster(plugin)):
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

    def displayName(self):
        return "Sync Plugins"

    def tooltip(self):
        return "Enables all Mods one at a time to match load order"

    def icon(self):
        return QIcon()

    def requirements(self):
        return [GamePluginsRequirement()]


def createPlugin() -> mobase.IPluginTool:
    return PluginSync()
