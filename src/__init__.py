from PyQt5.QtGui import QIcon
# from typing import List

import mobase

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
        return mobase.VersionInfo(0, 1, 0, mobase.ReleaseType.FINAL)

    def isActive(self):
        return True

    def settings(self):
        return []

    def display(self):
        allPlugins = self._pluginList.pluginNames()
        allPlugins = sorted(
            allPlugins,
            key=lambda
            plugin: self._modList.priority(self._pluginList.origin(plugin))
        )

        # Extract master files
        plugins = []
        masters = []
        for plugin in allPlugins:
            if (self._pluginList.isMaster(plugin)):
                masters.append(plugin)
            else:
                plugins.append(plugin)

        # Sort DLC correctly (Unmanaged Files)
        masters[0] = "Skyrim.esm"
        masters[1] = "Update.esm"
        masters[2] = "Dawnguard.esm"
        masters[3] = "HearthFires.esm"
        masters[4] = "Dragonborn.esm"

        # Merge masters into the plugin list at the begining
        allPlugins = masters + plugins


        # Set the new load order
        for priority, plugin in reversed(list(enumerate(allPlugins))):
            self._pluginList.setPriority(plugin, priority)

        # Not sure why this doesn't work
        # self._pluginList.setLoadOrder(allPlugins)

        # Refresh the UI
        self._organizer.refresh(save_changes=True)
        return True

    def displayName(self):
        return "Sync Plugins"

    def tooltip(self):
        return "Enables all Mods one at a time to match load order"

    def icon(self):
        return QIcon()


def createPlugin() -> mobase.IPluginTool:
    return PluginSync()
