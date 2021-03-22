from PyQt5.QtGui import QIcon
from typing import List

import mobase

class EnableByLoadOrder(mobase.IPluginTool):

	_organizer: mobase.IOrganizer
	_modList: mobase.IModList

	def __init__(self):
		super().__init__()

	def init(self, organizer: mobase.IOrganizer):
		self._organizer = organizer
		self._modList = organizer.modList()
		return True

	def name(self):
		return "Sync Load Order"

	def author(self):
		return "coldrifting"

	def description(self):
		return "Enables all mods in the left pane one at a time, so that they match the load order"

	def version(self):
		return mobase.VersionInfo(0, 1, 0, mobase.ReleaseType.FINAL)

	def isActive(self):
		return True

	def settings(self):
		return []

	def display(self):
		allMods = self._modList.allModsByProfilePriority()

		for modName in allMods:
			modClass = self._modList.getMod(modName)
			# Get Inactive mods that aren't separators
			if not (modClass.isSeparator()):
				if not (self._modList.state(modName) & mobase.ModState.ACTIVE):
						# Activate mods one at a time
						self._modList.setActive(modName, True)

		return True

	def displayName(self):
		return "Sync Load Order"

	def tooltip(self):
		return "Enables all Mods one at a time to match load order"

	def icon(self):
		return QIcon()

def createPlugin() -> mobase.IPluginTool:
	return EnableByLoadOrder()