# -*- coding: utf-8 -*-

# UserSkin, based on AtileHD concept by schomi & plnick
#
# maintainer: j00zek
# Modified  : RAED
#
# extension for openpli, all skins, descriptions, bar selections and other @j00zek 2014/2015
# Uszanuj czyj¹œ pracê i NIE przyw³aszczaj sobie autorstwa!

#This plugin is free software, you are allowed to
#modify it (if you keep the license),
#but you are not allowed to distribute/publish
#it without source code (this version and your modifications).
#This means you also have to distribute
#source code of your modifications.

from debug import printDEBUG
from inits import *

from Components.ActionMap import ActionMap
from Components.config import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from enigma import ePicLoad
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import *
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
#system imports
from os import listdir, remove, rename, system, path, symlink, chdir, rmdir, mkdir
import shutil
import re

#Translations part
from Components.Language import language
currLang = language.getLanguage()[:2] #used for descriptions keep GUI language in 'pl|en' format
from translate import _

#AtileHD permanent configs, we use AtileHD for compatibility reasons
config.plugins.AtileHD = ConfigSubsection()
config.plugins.AtileHD.refreshInterval = ConfigNumber(default=30) #in minutes
config.plugins.AtileHD.woeid = ConfigNumber(default=523920) #Location Warsaw (visit weather.yahoo.com)
config.plugins.AtileHD.tempUnit = ConfigSelection(default="Celsius", choices = [
                ("Celsius", _("Celsius")),
                ("Fahrenheit", _("Fahrenheit"))
                ])
config.plugins.AtileHD = ConfigSubsection()
config.plugins.AtileHD.refreshInterval = ConfigNumber(default=30) #in minutes
config.plugins.AtileHD.woeid = ConfigNumber(default=523920) #Location Warsaw (visit weather.yahoo.com)
config.plugins.AtileHD.tempUnit = ConfigSelection(default="Celsius", choices = [
                ("Celsius", _("Celsius")),
                ("Fahrenheit", _("Fahrenheit"))
                ])
       
#def Plugins(**kwargs):
#    return [PluginDescriptor(name=_("AtileHD Setup"), description=_("Personalize your Skin"), where = PluginDescriptor.WHERE_MENU, icon="plugin.png", fnc=menu)]

#def menu(menuid, **kwargs):
#    if menuid == "vtimain" or menuid == "system":
#        return [(_("Setup - AtileHD"), main, "AtileHD_setup", 40)]
#    return []

#def main(session, **kwargs):
#    printDEBUG("Opening config ...")
#    session.open(AtileHD_Config)

class AtileHD_Config(Screen, ConfigListScreen):
    skin = """
  <screen name="AtileHD_Config" position="82,124" size="1101,376" title="AtileHD Setup" backgroundColor="transparent" flags="wfNoBorder">
    <eLabel position="7,2" size="1091,372" zPosition="-15" backgroundColor="#20000000" />
    <eLabel position="4,51" size="664,238" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="672,51" size="410,237" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="6,302" size="240,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="284,302" size="240,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="564,302" size="240,56" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="843,302" size="240,55" zPosition="-10" backgroundColor="#202673ec" />
    <widget source="Title" render="Label" position="2,4" size="889,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <widget name="config" position="6,55" size="657,226" scrollbarMode="showOnDemand" transparent="1" />
    <widget name="Picture" position="676,56" size="400,225" alphatest="blend" />
    <widget name="key_red" position="18,316" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget name="key_green" position="299,317" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget name="key_yellow" position="578,317" size="210,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#209ca81b" transparent="1" />
    <widget name="key_blue" position="854,318" size="210,25" zPosition="0" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#202673ec" transparent="1" />
  </screen>
"""

    skin_lines = []
    changed_screens = False
        
    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        
        myTitle=_("SphereFHD Setup %s") % AtileHDInfo
        self.setTitle(myTitle)
        try:
            self["title"]=StaticText(myTitle)
        except:
            pass
            
        self.skin_base_dir = SkinPath
        self.currentSkin = CurrentSkinName
        printDEBUG("self.skin_base_dir=%s, skin=%s, currentSkin=%s" % (self.skin_base_dir, config.skin.primary_skin.value, self.currentSkin))
        if self.currentSkin != '':
                self.currentSkin = '_' + self.currentSkin # default_skin = '', others '_skinname', used later
                
        if path.exists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/VTIPanel/')):
            self.isVTI = True
        else:
            self.isVTI = False
            
        self.defaultOption = "default"
        self.defaults = (self.defaultOption, _("Default"))
        self.color_file = "skin_user_colors.xml"
        self.windowstyle_file = "skin_user_window.xml"
        self.user_font_file = "skin_user_header.xml"
        self.user_bar_link = 'skin_user_bar'
        
        if path.exists(self.skin_base_dir):
            #FONTS
            if path.exists(self.skin_base_dir + self.user_font_file):
                self.default_font_file = path.basename(path.realpath(self.skin_base_dir + self.user_font_file))
                printDEBUG("self.default_font_file = " + self.default_font_file )
            else:
                self.default_font_file = self.defaultOption
            if not path.exists(self.skin_base_dir + "allFonts/"):
                mkdir(self.skin_base_dir + "allFonts/")
            #COLORS
            if path.exists(self.skin_base_dir + self.color_file):
                self.default_color_file = path.basename(path.realpath(self.skin_base_dir + self.color_file))
                printDEBUG("self.default_color_file = " + self.default_color_file )
            else:
                self.default_color_file = self.defaultOption
                
            if not path.exists(self.skin_base_dir + "allColors/"):
                mkdir(self.skin_base_dir + "allColors/")
            #WINDOWS
            if path.exists(self.skin_base_dir + self.color_file):
                self.default_windowstyle_file = path.basename(path.realpath(self.skin_base_dir + self.windowstyle_file))
                printDEBUG("self.default_windowstyle_file = " + self.default_windowstyle_file )
            else:
                self.default_windowstyle_file = self.defaultOption
                
            if not path.exists(self.skin_base_dir + "allWindows/"):
                mkdir(self.skin_base_dir + "allWindows/")
            #PREVIEW
            if not path.exists(self.skin_base_dir + "allPreviews"):
                mkdir(self.skin_base_dir + "allPreviews/")
            if path.exists(self.skin_base_dir + "preview"):
                if self.isVTI == False and path.isdir(self.skin_base_dir + "preview"):
                    try: rmdir(self.skin_base_dir + "preview")
                    except: pass
            else:
                if self.isVTI == True:
                    symlink(self.skin_base_dir + "allPreviews", self.skin_base_dir + "preview")
            #SELECTOR
            if not path.exists(self.skin_base_dir + "allBars"):
                mkdir(self.skin_base_dir + "allBars/")
            if path.exists(self.skin_base_dir + self.user_bar_link):
                self.default_user_bar_link = path.basename(path.realpath(self.skin_base_dir + self.user_bar_link))
                printDEBUG("self.user_bar_link = " + self.default_user_bar_link )
            else:
                self.default_user_bar_link = self.defaultOption
            #DESCRIPTIONS
            if not path.exists(self.skin_base_dir + "allInfos"):
                mkdir(self.skin_base_dir + "allInfos/")
            #SELECTED Skins folder - We use different folder name (more meaningfull) for selections
            if path.exists(self.skin_base_dir + "mySkin_off"):
                if not path.exists(self.skin_base_dir + "AtileHD_Selections"):
                    chdir(self.skin_base_dir)
                    try:
                        rename("mySkin_off", "AtileHD_Selections")
                    except:
                        pass

        current_color = self.getCurrentColor()[0]
        current_windowstyle = self.getCurrentWindowstyle()[0]
        current_font = self.getCurrentFont()[0]
        current_bar = self.getCurrentBar()[0]
        myAtileHD_active = self.getmySkinState()
        self.myAtileHD_active = NoSave(ConfigYesNo(default=myAtileHD_active))
        self.myAtileHD_font = NoSave(ConfigSelection(default=current_font, choices = self.getPossibleFont()))
        self.myAtileHD_style = NoSave(ConfigSelection(default=current_color, choices = self.getPossibleColor()))
        self.myAtileHD_windowstyle = NoSave(ConfigSelection(default=current_windowstyle, choices = self.getPossibleWindowstyle()))
        self.myAtileHD_bar = NoSave(ConfigSelection(default=current_bar, choices = self.getPossibleBars()))
        
        self.myAtileHD_fake_entry = NoSave(ConfigNothing())
        self.LackOfFile = ''
        
        self.list = []
        ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)

        self["key_red"] = Label(_("Cancel"))
        self["key_green"] = Label(_("OK"))
        self["key_yellow"] = Label()
        self["key_blue"] = Label()
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "green": self.keyOk,
                "red": self.cancel,
                "yellow": self.keyYellow,
                "blue": self.keyBlue,
                "cancel": self.cancel,
                "ok": self.keyOk,
            }, -2)
            
        self["Picture"] = Pixmap()
        
        if not self.selectionChanged in self["config"].onSelectionChanged:
            self["config"].onSelectionChanged.append(self.selectionChanged)
        
        self.createConfigList()
        self.updateEntries = False
        
    def createConfigList(self):
        #self.set_bar = getConfigListEntry(_("Selector bar style:"), self.myAtileHD_bar)
        self.set_color = getConfigListEntry(_("Colors:"), self.myAtileHD_style)
        #self.set_windowstyle = getConfigListEntry(_("Window style:"), self.myAtileHD_windowstyle)
        self.set_font = getConfigListEntry(_("Font:"), self.myAtileHD_font)
        self.set_myatile = getConfigListEntry(_("Enable skin personalization:"), self.myAtileHD_active)
        self.list = []
        self.list.append(self.set_myatile)
        self.list.append(self.set_color)
        #self.list.append(self.set_windowstyle)
        self.list.append(self.set_font)
        #self.list.append(self.set_bar)
        self.list.append(getConfigListEntry(_("---Yahoo Weather---"), self.myAtileHD_fake_entry))
        self.list.append(getConfigListEntry(_("Refresh interval in minutes:"), config.plugins.AtileHD.refreshInterval))
        self.list.append(getConfigListEntry(_("Location # (http://weather.yahoo.com/):"), config.plugins.AtileHD.woeid))
        self.list.append(getConfigListEntry(_("Temperature unit:"), config.plugins.AtileHD.tempUnit))
        self["config"].list = self.list
        self["config"].l.setList(self.list)
        if self.myAtileHD_active.value:
            self["key_yellow"].setText(_("User skins"))
            self["key_blue"].setText(_("Extract from skin.xml"))
        else:
            self["key_yellow"].setText("")
            self["key_blue"].setText("")

    def changedEntry(self):
        self.updateEntries = True
        printDEBUG("[SphereFHD:changedEntry]")
        if self["config"].getCurrent() == self.set_color:
            self.setPicture(self.myAtileHD_style.value)
        #elif self["config"].getCurrent() == self.set_windowstyle:
        #    self.setPicture(self.myAtileHD_windowstyle.value)
        elif self["config"].getCurrent() == self.set_font:
            self.setPicture(self.myAtileHD_font.value)
        #elif self["config"].getCurrent() == self.set_bar:
        #    self.setPicture(self.myAtileHD_bar.value)
        elif self["config"].getCurrent() == self.set_myatile:
            if self.myAtileHD_active.value:
                self["key_yellow"].setText(_("User skins"))
            else:
                self["key_yellow"].setText("")

    def selectionChanged(self):
        if self["config"].getCurrent() == self.set_color:
            self.setPicture(self.myAtileHD_style.value)
        #elif self["config"].getCurrent() == self.set_windowstyle:
        #    self.setPicture(self.myAtileHD_windowstyle.value)
        elif self["config"].getCurrent() == self.set_font:
            self.setPicture(self.myAtileHD_font.value)
        #elif self["config"].getCurrent() == self.set_bar:
        #    self.setPicture(self.myAtileHD_bar.value)
        else:
            self["Picture"].hide()

    def cancel(self):
        if self["config"].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Save settings?"), MessageBox.TYPE_YESNO, default = False)
        else:
            for x in self["config"].list:
                x[1].cancel()
            if self.changed_screens:
                self.restartGUI()
            else:
                self.close()

    def cancelConfirm(self, result):
        if result is None or result is False:
            printDEBUG("Cancel confirmed.")
        else:
            printDEBUG("Cancel confirmed. Config changes will be lost.")
            for x in self["config"].list:
                x[1].cancel()
            self.close()
                
    def getPossibleColor(self):
        color_list = []
        color_list.append(self.defaults)
        
        if not path.exists(self.skin_base_dir + "allColors/"):
            return color_list
        
        for f in sorted(listdir(self.skin_base_dir + "allColors/"), key=str.lower):
            if f.endswith('.xml') and f.startswith('colors_'):
                friendly_name = f.replace("colors_atile_", "").replace("colors_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                color_list.append((f, friendly_name))
        
        for f in sorted(listdir(self.skin_base_dir), key=str.lower):
            if f.endswith('.xml') and f.startswith('colors_'):
                friendly_name = f.replace("colors_atile_", "").replace("colors_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                color_list.append((f, friendly_name))

        return color_list

    def getPossibleWindowstyle(self):
        windowstyle_list = []
        windowstyle_list.append(self.defaults)
        
        if not path.exists(self.skin_base_dir + "allWindows/"):
            return windowstyle_list
        
        for f in sorted(listdir(self.skin_base_dir + "allWindows/"), key=str.lower):
            if f.endswith('.xml') and f.startswith('window_'):
                friendly_name = f.replace("window_atile_", "").replace("window_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                windowstyle_list.append((f, friendly_name))
        
        for f in sorted(listdir(self.skin_base_dir), key=str.lower):
            if f.endswith('.xml') and f.startswith('window_'):
                friendly_name = f.replace("window_atile_", "").replace("window_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                windowstyle_list.append((f, friendly_name))

        return windowstyle_list		

    def getPossibleFont(self):
        font_list = []
        font_list.append(self.defaults)
        
        if not path.exists(self.skin_base_dir + "allFonts/"):
            return font_list
        
        for f in sorted(listdir(self.skin_base_dir + "allFonts/"), key=str.lower):
            if f.endswith('.xml') and f.startswith('font_'):
                friendly_name = f.replace("font_atile_", "").replace("font_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                font_list.append((f, friendly_name))

        for f in sorted(listdir(self.skin_base_dir), key=str.lower):
            if f.endswith('.xml') and f.startswith('font_'):
                friendly_name = f.replace("font_atile_", "").replace("font_", "")
                friendly_name = friendly_name.replace(".xml", "")
                friendly_name = friendly_name.replace("_", " ")
                font_list.append((f, friendly_name))

        return font_list

    def getmySkinState(self):
        chdir(self.skin_base_dir)
        if path.exists("mySkin"):
            return True
        else:
            return False

    def getCurrentColor(self):
        myfile = self.skin_base_dir + self.color_file
        if not path.exists(myfile):
            if path.exists(self.skin_base_dir + "allColors/" + self.default_color_file):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink("allColors/" + self.default_color_file, self.color_file)
            else:
                return (self.default_color_file, self.default_color_file)
        filename = path.realpath(myfile)
        filename = path.basename(filename)
        friendly_name = filename.replace("colors_atile_", "").replace("colors_", "")
        friendly_name = friendly_name.replace(".xml", "")
        friendly_name = friendly_name.replace("_", " ")
        return (filename, friendly_name)

    def getCurrentWindowstyle(self):
        myfile = self.skin_base_dir + self.windowstyle_file
        if not path.exists(myfile):
            if path.exists(self.skin_base_dir + "allWindows/" + self.default_windowstyle_file):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink("allWindows/" + self.default_windowstyle_file, self.windowstyle_file)
            else:
                return (self.default_windowstyle_file, self.default_windowstyle_file)
        filename = path.realpath(myfile)
        filename = path.basename(filename)
        friendly_name = filename.replace("window_atile_", "").replace("window_", "")
        friendly_name = friendly_name.replace(".xml", "")
        friendly_name = friendly_name.replace("_", " ")
        return (filename, friendly_name)
		
    def getCurrentFont(self):
        myfile = self.skin_base_dir + self.user_font_file
        if not path.exists(myfile):
            if path.exists(self.skin_base_dir + "allFonts/" + self.default_font_file):
                if path.islink(myfile):
                    remove(myfile)
                chdir(self.skin_base_dir)
                symlink("allFonts/" + self.default_font_file, self.user_font_file)
            else:
                return (self.default_font_file, self.default_font_file)
        filename = path.realpath(myfile)
        filename = path.basename(filename)
        friendly_name = filename.replace("font_atile_", "").replace("font_", "")
        friendly_name = friendly_name.replace(".xml", "")
        friendly_name = friendly_name.replace("_", " ")
        return (filename, friendly_name)

    def setPicture(self, f):
        preview = self.skin_base_dir + "allPreviews/"
        if not path.exists(preview):
            mkdir(preview)
        pic = f[:-4]
        if f.startswith("bar_"):
            pic = f + ".png"
        printDEBUG("[SphereFHD:setPicture] pic =" + pic + '[jpg|png]')
        previewJPG = preview + "preview_" + picJPG
        if path.exists(preview + "preview_" + pic + '.jpg'):
            self.UpdatePreviewPicture(preview + "preview_" + pic + '.jpg')
        if path.exists(preview + "preview_" + pic + '.png'):
            self.UpdatePreviewPicture(preview + "preview_" + pic + '.png')
        else:
            self["Picture"].hide()

    def setPicture(self, f):
        pic = f[:-4]
        if path.exists(self.skin_base_dir + "allPreviews/preview_" + pic + '.png'):
            self.UpdatePreviewPicture(self.skin_base_dir + "allPreviews/preview_" + pic + '.png')
        elif path.exists(self.skin_base_dir + "allPreviews/preview_" + pic + '.jpg'):
            self.UpdatePreviewPicture(self.skin_base_dir + "allPreviews/preview_" + pic + '.jpg')
        elif path.exists(self.skin_base_dir + "allPreviews/" + pic + '.png'):
            self.UpdatePreviewPicture(self.skin_base_dir + "allPreviews/" + pic + '.png')
        elif path.exists(self.skin_base_dir + "allPreviews/" + pic + '.jpg'):
            self.UpdatePreviewPicture(self.skin_base_dir + "allPreviews/" + pic + '.jpg')
    
    def UpdatePreviewPicture(self, PreviewFileName):
            self["Picture"].instance.setScale(1)
            self["Picture"].instance.setPixmap(LoadPixmap(path=PreviewFileName))
            self["Picture"].show()
            
    def keyYellow(self):
        if self.myAtileHD_active.value:
            if not path.exists(self.skin_base_dir + "AtileHD_Selections"):
                mkdir(self.skin_base_dir + "AtileHD_Selections")
            if not path.exists(self.skin_base_dir + "allPreviews"):
                mkdir(self.skin_base_dir + "allPreviews")
            self.session.openWithCallback(self.AtileHDScreesnCB, AtileHDScreens)
        else:
            self["config"].setCurrentIndex(0)

    def keyOk(self):
        if self["config"].isChanged() or self.updateEntries == True:
            printDEBUG("[SphereFHD:keyOk] self.myAtileHD_font.value=" + self.myAtileHD_font.value)
            printDEBUG("[SphereFHD:keyOk] self.myAtileHD_style.value=" + self.myAtileHD_style.value)
            printDEBUG("[SphereFHD:keyOk] self.myAtileHD_windowstyle.value=" + self.myAtileHD_windowstyle.value)
            printDEBUG("[SphereFHD:keyOk] self.myAtileHD_bar.value=" + self.myAtileHD_bar.value)
            config.plugins.AtileHD.refreshInterval.value = config.plugins.AtileHD.refreshInterval.value
            config.plugins.AtileHD.woeid.value = config.plugins.AtileHD.woeid.value
            config.plugins.AtileHD.tempUnit.value = config.plugins.AtileHD.tempUnit.value
            for x in self["config"].list:
                x[1].save()
            configfile.save()
            #we change current folder to active skin folder
            chdir(self.skin_base_dir)
            #FONTS
            if path.exists(self.user_font_file):
                remove(self.user_font_file)
            elif path.islink(self.user_font_file):
                remove(self.user_font_file)
            if path.exists('allFonts/' + self.myAtileHD_font.value):
                symlink('allFonts/' + self.myAtileHD_font.value, self.user_font_file)
            #COLORS
            if path.exists(self.color_file):
                remove(self.color_file)
            elif path.islink(self.color_file):
                remove(self.color_file)
            if path.exists("allColors/" + self.myAtileHD_style.value):
                symlink("allColors/" + self.myAtileHD_style.value, self.color_file)
            #WINDOWS
            if path.exists(self.windowstyle_file):
                remove(self.windowstyle_file)
            elif path.islink(self.windowstyle_file):
                remove(self.windowstyle_file)
            if path.exists("allWindows/" + self.myAtileHD_windowstyle.value):
                symlink("allWindows/" + self.myAtileHD_windowstyle.value, self.windowstyle_file)
            #SELECTOR
            if path.exists(self.user_bar_link):
                remove(self.user_bar_link)
            elif path.islink(self.user_bar_link):
                remove(self.user_bar_link)
            if path.exists("allBars/" + self.myAtileHD_bar.value):
                symlink("allBars/" + self.myAtileHD_bar.value , self.user_bar_link)
                sourcePath = path.join(self.skin_base_dir , self.user_bar_link)
                destFolder = self.myAtileHD_bar.value.split(".", 1)[1]
                destPath = path.join(self.skin_base_dir , destFolder)
                printDEBUG("[SphereFHD:keyOk]cp -fr %s %s" % (sourcePath,destPath))
                with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") #avoid GS with system on tuners with small RAM
                printDEBUG("[SphereFHD:keyOk]cp -fr %s/* %s/" % (sourcePath,destPath))
                system("cp -fr %s/* %s/" %(sourcePath,destPath)) #for safety, nicely manage overwrite ;)
            #SCREENS
            if self.myAtileHD_active.value:
                if not path.exists("mySkin") and path.exists("AtileHD_Selections"):
                    try:
                        symlink("AtileHD_Selections","mySkin")
                    except:
                        printDEBUG("[SphereFHD:keyOK]symlinking myskin exception")
                        with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n") #avoid GS with system on tuners with small RAM
                        destPath = path.join(self.skin_base_dir , "mySkin")
                        sourcePath = path.join(self.skin_base_dir , "AtileHD_Selections")
                        system("rm -rf %s;ln -sf %s %s" % (destPath , sourcePath ,destPath) )
            else:
                if path.exists("mySkin"):
                    if path.exists("AtileHD_Selections"):
                        if path.islink("mySkin"):
                            remove("mySkin")
                        else:
                            shutil.rmtree("mySkin")
                    else:
                        rename("mySkin", "AtileHD_Selections")
  
            self.update_user_skin()
            self.restartGUI()
        else:
            if self.changed_screens:
                self.update_user_skin()
                self.restartGUI()
            else:
                self.close()

    def AtileHDScreesnCB(self):
        self.changed_screens = True
        self["config"].setCurrentIndex(0)

    def restartGUI(self):
        myMessage = ''
        if self.LackOfFile != '':
            printDEBUG("missing components: %s" % self.LackOfFile)
            myMessage += _("Missing components found: %s\n\n") % self.LackOfFile
            myMessage += _("Skin will NOT work properly!!!\n\n")
        myMessage += _("Restart necessary, restart GUI now?")
        restartbox = self.session.openWithCallback(self.restartGUIcb,MessageBox, myMessage, MessageBox.TYPE_YESNO, default = False)
        restartbox.setTitle(_("Message"))

    def keyBlue(self):
        import xml.etree.cElementTree as ET
        from Screens.VirtualKeyBoard import VirtualKeyBoard
        
        def SaveScreen(ScreenFileName = None):
            if ScreenFileName is not None:
                if not ScreenFileName.endswith('.xml'):
                    ScreenFileName += '.xml'
                if not ScreenFileName.startswith('skin_'):
                    ScreenFileName = 'skin_' + ScreenFileName
                printDEBUG("Writing %s%s/%s" % (SkinPath, 'allScreens',ScreenFileName))
                
                for skinScreen in root.findall('screen'):
                    if 'name' in skinScreen.attrib:
                        if skinScreen.attrib['name'] == self.ScreenSelectedToExport:
                            SkinContent = ET.tostring(skinScreen)
                            break
                with open("%s%s/%s" % (SkinPath, 'allScreens', ScreenFileName), "w") as f:
                    f.write('<skin>\n')
                    f.write(SkinContent)
                    f.write('</skin>\n')

        def ScreenSelected(ret):
            if ret:
                self.ScreenSelectedToExport = ret[0]
                printDEBUG('Selected: %s' % self.ScreenSelectedToExport)
                self.session.openWithCallback(SaveScreen, VirtualKeyBoard, title=(_("Enter filename")), text = self.ScreenSelectedToExport + '_new')
        
        ScreensList= []
        root = ET.parse(SkinPath + 'skin.xml').getroot()
        for skinScreen in root.findall('screen'):
            if 'name' in skinScreen.attrib:
                printDEBUG('Found in skin.xml: %s' % skinScreen.attrib['name'])
                ScreensList.append((skinScreen.attrib['name'],skinScreen.attrib['name']))
        if len(ScreensList) > 0:
            ScreensList.sort()
            self.session.openWithCallback(ScreenSelected, ChoiceBox, title = _("Select skin to export:"), list = ScreensList)
                
    def restartGUIcb(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def update_user_skin(self):
        #print "[AtileHD} update_user_skin"
        if self.isVTI == True: #jesli mamy VTI, to nie musimy robic pliku
            return

        user_skin_file=resolveFilename(SCOPE_CONFIG, 'skin_user' + self.currentSkin + '.xml')
        if path.exists(user_skin_file):
            remove(user_skin_file)
        if self.myAtileHD_active.value:
            printDEBUG("update_user_skin.self.myAtileHD_active.value")
            user_skin = ""
            if path.exists(self.skin_base_dir + 'skin_user_header.xml'):
                user_skin = user_skin + self.readXMLfile(self.skin_base_dir + 'skin_user_header.xml' , 'fonts')
            if path.exists(self.skin_base_dir + 'skin_user_colors.xml'):
                user_skin = user_skin + self.readXMLfile(self.skin_base_dir + 'skin_user_colors.xml' , 'ALLSECTIONS')
            if path.exists(self.skin_base_dir + 'skin_user_window.xml'):
                user_skin = user_skin + self.readXMLfile(self.skin_base_dir + 'skin_user_window.xml' , 'ALLSECTIONS')
            if path.exists(self.skin_base_dir + 'mySkin'):
                for f in listdir(self.skin_base_dir + "mySkin/"):
                    user_skin = user_skin + self.readXMLfile(self.skin_base_dir + "mySkin/" + f, 'screen')
            if user_skin != '':
                user_skin = "<skin>\n" + user_skin
                user_skin = user_skin + "</skin>\n"
                with open (user_skin_file, "w") as myFile:
                    printDEBUG("update_user_skin.self.myAtileHD_active.value write myFile")
                    myFile.write(user_skin)
                    myFile.flush()
                    myFile.close()
            #checking if all renderers are in system
            self.checkComponent(user_skin, 'render' , resolveFilename(SCOPE_PLUGINS, '../Components/Renderer/') )
            self.checkComponent(user_skin, 'pixmap' , resolveFilename(SCOPE_SKIN, '') )
               
    def checkComponent(self, myContent, look4Component , myPath): #look4Component=render|
        def updateLackOfFile(name, mySeparator =', '):
            printDEBUG("Missing component found:%s\n" % name)
            if self.LackOfFile == '':
                self.LackOfFile = name
            else:
                self.LackOfFile += mySeparator + name
            
        r=re.findall( r' %s="([a-zA-Z0-9_/\.]+)" ' % look4Component , myContent )
        r=list(set(r)) #remove duplicates, no need to check for the same component several times

        printDEBUG("Found %s:\n" % (look4Component))
        print r
        if r:
            for myComponent in set(r):
                #print" [AtileHD] checks if %s exists" % myComponent
                if look4Component == 'pixmap':
                    #printDEBUG("%s\n%s\n" % (myComponent,myPath + myComponent))
                    if myComponent.startswith('/'):
                        if not path.exists(myComponent):
                            updateLackOfFile(myComponent, '\n')
                    else:
                        if not path.exists(myPath + myComponent):
                            updateLackOfFile(myComponent)
                else:
                    if not path.exists(myPath + myComponent + ".pyo") and not path.exists(myPath + myComponent + ".py"):
                        updateLackOfFile(myComponent)
        return
    
    def readXMLfile(self, XMLfilename, XMLsection): #sections:ALLSECTIONS|fonts|
        myPath=path.realpath(XMLfilename)
        if not path.exists(myPath):
            remove(XMLfilename)
            return ''
        filecontent = ''
        if XMLsection == 'ALLSECTIONS':
            sectionmarker = True
        else:
            sectionmarker = False
        with open (XMLfilename, "r") as myFile:
            for line in myFile:
                if line.find('<skin>') >= 0 or line.find('</skin>') >= 0:
                    continue
                if line.find('<%s' %XMLsection) >= 0 and sectionmarker == False:
                    sectionmarker = True
                elif line.find('</%s>' %XMLsection) >= 0 and sectionmarker == True:
                    sectionmarker = False
                    filecontent = filecontent + line
                if sectionmarker == True:
                    filecontent = filecontent + line
            myFile.close()
        return filecontent

##### userBARs #####        
    def getCurrentBar(self):
        myfile = self.skin_base_dir + self.user_bar_link
        printDEBUG("[SphereFHD:getCurrentBar] myfile='%s'" % myfile)
        if not path.exists(myfile):
            return (self.default_user_bar_link, self.default_user_bar_link)
        else:
            filename = path.realpath(myfile)
            filename = path.basename(filename)
            friendly_name = filename.replace("bar_", "").replace("_", " ")
            return (filename, friendly_name)

    def getPossibleBars(self):
        #printDEBUG("[SphereFHD:getPossibleBars] >>>")
        bar_list = []
        if not listdir(self.skin_base_dir + "allBars/"):
            bar_list.append(self.defaults)
            return bar_list
    
        for f in sorted(listdir(self.skin_base_dir + "allBars/"), key=str.lower):
            fpath = path.join(self.skin_base_dir + "allBars/", f)
            printDEBUG("[SphereFHD:getPossibleBars] f='%s'" % f)
            if path.isdir(fpath) and f.startswith('bar_') and f.find('.') > 1:
                friendly_name = f.split(".", 1)[0]
                friendly_name = friendly_name.replace("bar_", "").replace("_", " ")
                bar_list.append((f, _(friendly_name)))
        return bar_list

class AtileHDScreens(Screen):
    skin = """
  <screen name="AtileHDScreens" position="0,0" size="1280,720" title="AtileHD Setup" backgroundColor="transparent" flags="wfNoBorder">
    <eLabel position="0,0" size="1280,720" zPosition="-15" backgroundColor="#20000000" />
    <eLabel position=" 55,100" size="725,515" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="785,295" size="445,320" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="785,100" size="135,190" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position="925,100" size="305,190" zPosition="-10" backgroundColor="#20606060" />
    <eLabel position=" 55,620" size="290,55" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,620" size="290,55" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,620" size="290,55" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,620" size="290,55" zPosition="-10" backgroundColor="#202673ec" />
    <eLabel position=" 55,675" size="290, 5" zPosition="-10" backgroundColor="#20b81c46" />
    <eLabel position="350,675" size="290, 5" zPosition="-10" backgroundColor="#20009f3c" />
    <eLabel position="645,675" size="290, 5" zPosition="-10" backgroundColor="#209ca81b" />
    <eLabel position="940,675" size="290, 5" zPosition="-10" backgroundColor="#202673ec" />
    <!--widget source="session.VideoPicture" render="Pig" position="935,115" zPosition="3" size="284,160" backgroundColor="#ff000000">
    </widget-->
    <widget source="Title" render="Label" position="70,47" size="950,43" font="Regular;35" foregroundColor="#00ffffff" backgroundColor="#004e4e4e" transparent="1" />
    <widget source="menu" render="Listbox" position="70,115" size="700,480" scrollbarMode="showOnDemand" transparent="1">
      <convert type="TemplatedMultiContent">
                                {"template":
                                        [
                                                MultiContentEntryPixmapAlphaTest(pos = (2, 2), size = (54, 54), png = 3),
                                                MultiContentEntryText(pos = (60, 2), size = (500, 22), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1), # name
                                                MultiContentEntryText(pos = (55, 24),size = (500, 32), font=1, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 2), # info
                                        ],
                                        "fonts": [gFont("Regular", 22),gFont("Regular", 16)],
                                        "itemHeight": 60
                                }
                        </convert>
    </widget>
    <widget name="PreviewPicture" position="808,342" size="400,225" alphatest="on" />
    <widget source="key_red" render="Label" position="70,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20b81c46" transparent="1" />
    <widget source="key_green" render="Label" position="365,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" backgroundColor="#20009f3c" transparent="1" />
    <widget source="key_yellow" render="Label" position="650,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" transparent="1" />
    <widget source="key_blue" render="Label" position="950,635" size="260,25" zPosition="1" font="Regular;20" halign="left" foregroundColor="#00ffffff" transparent="1" />
  </screen>
"""

    EditScreen = False
    DeleteScreen = False
    
    allScreensGroups = [(_("All skins"), "_"),
    (_("ChannelList skins"), "channelselection"),
    (_("Infobar skins"), "infobar"),
    ]

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        myTitle=_("SphereFHD %s - additional screens") %  AtileHDInfo
        self.setTitle(myTitle)
        try:
            self["title"]=StaticText(myTitle)
        except:
            pass
        
        self["key_red"] = StaticText(_("Exit"))
        self["key_green"] = StaticText("")
        self["key_yellow"] = StaticText("")
        self["key_blue"] = StaticText(_("Settings"))
        
        self["PreviewPicture"] = Pixmap()
        
        menu_list = []
        self["menu"] = List(menu_list)
        
        self.allScreensGroup = self.allScreensGroups[0][1]
        
        self["shortcuts"] = ActionMap(["SetupActions", "ColorActions", "DirectionActions"],
        {
            "ok": self.runMenuEntry,
            "cancel": self.keyCancel,
            "red": self.keyCancel,
            "green": self.keyGreen,
            "blue": self.keyBlue,
            "yellow": self.keyYellow,
        }, -2)
        
        self.currentSkin = CurrentSkinName
        self.skin_base_dir = SkinPath
        #self.screen_dir = "allScreens"
        self.allScreens_dir = "allScreens"
        self.file_dir = "AtileHD_Selections"
        if path.exists("%sAtileHDpics/install.png" % SkinPath):
            printDEBUG("SkinConfig is loading %sAtileHDpics/install.png" % SkinPath)
            self.enabled_pic = LoadPixmap(cached=True, path="%sAtileHDpics/install.png" % SkinPath)
        else:
            self.enabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/SphereFHD/pic/install.png"))
        #check if we have preview files
        isPreview=0
        for xpreview in listdir(self.skin_base_dir + "allPreviews/"):
            if len(xpreview) > 4 and  xpreview[-4:] == ".png":
                isPreview += 1
            if isPreview >= 2:
                break
        if self.currentSkin == "infinityHD-nbox-tux-full" and isPreview < 2:
            printDEBUG("no preview files :(")
            if path.exists("%sAtileHDpics/install.png" % SkinPath):
                printDEBUG("SkinConfig is loading %sAtileHDpics/opkg.png" % SkinPath)
                self.disabled_pic = LoadPixmap(cached=True, path="%sAtileHDpics/opkg.png" % SkinPath)
            else:
                self.disabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/SphereFHD/pic/opkg.png"))
            self['key_blue'].setText(_('Install from OPKG'))
        else:
            if path.exists("%sAtileHDpics/install.png" % SkinPath):
                printDEBUG("SkinConfig is loading %sAtileHDpics/remove.png" % SkinPath)
                self.disabled_pic = LoadPixmap(cached=True, path="%sAtileHDpics/remove.png" % SkinPath)
            else:
                self.disabled_pic = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, "Extensions/SphereFHD/pic/remove.png"))
        
        if not self.selectionChanged in self["menu"].onSelectionChanged:
            self["menu"].onSelectionChanged.append(self.selectionChanged)
        
        self.onLayoutFinish.append(self.createMenuList)

    def keyBlue(self):
            #self.session.openWithCallback(self.endrun , MessageBox,_("To see previews install enigma2-skin-infinityhd-nbox-tux-full-preview package"), type = MessageBox.TYPE_INFO)
            #self.session.open(MessageBox,_("To see previews install package:\nenigma2-skin-infinityhd-nbox-tux-full-preview"), type = MessageBox.TYPE_INFO)
            self.session.openWithCallback(self.keyBlueEnd, ChoiceBox, title = _("Display..."), list = self.allScreensGroups)
            return

    def keyBlueEnd(self, ret):
        if ret:
            self.allScreensGroup = ret[1]
        else:
            self.allScreensGroup = '_'
        self.createMenuList()
        
    def endrun(self):
        return
     
    def selectionChanged(self):
        print "> self.selectionChanged"
        sel = self["menu"].getCurrent()
        self.setPicture(sel[0])
        #print sel
        if sel[3] == self.enabled_pic:
            #self["key_green"].setText("")
            #self.EditScreen = False
            self["key_green"].setText(_("Edit"))
            self.EditScreen = True
            self["key_yellow"].setText("")
            self.DeleteScreen = False
        elif sel[3] == self.disabled_pic:
            self["key_green"].setText(_("Edit"))
            self.EditScreen = True
            self["key_yellow"].setText(_("Delete"))
            self.DeleteScreen = True

    def createMenuList(self):
        chdir(self.skin_base_dir)
        f_list = []
        #printDEBUG('createMenuList> listing ' + self.skin_base_dir + self.allScreens_dir)
        if path.exists(self.skin_base_dir + self.allScreens_dir):
            list_dir = sorted(listdir(self.skin_base_dir + self.allScreens_dir), key=str.lower)
            for f in list_dir:
                if f.endswith('.xml') and f.startswith('skin_') and f.lower().find(self.allScreensGroup) > 0:
                    friendly_name = f.replace("skin_", "")
                    friendly_name = friendly_name.replace(".xml", "")
                    friendly_name = friendly_name.replace("_", " ")
                    linked_file = self.skin_base_dir + self.file_dir + "/" + f
                    if path.exists(linked_file):
                        if path.islink(linked_file):
                            pic = self.enabled_pic
                        else:
                            remove(linked_file)
                            symlink(self.skin_base_dir + self.allScreens_dir + "/" + f, self.skin_base_dir + self.file_dir + "/" + f)
                            pic = self.enabled_pic
                    else:
                        pic = self.disabled_pic
                    f_list.append((f, friendly_name, self.getInfo(f) , pic))
        menu_list = []
        if len(f_list) == 0:
            f_list.append(("dummy", _("No User skins found"), '', self.disabled_pic))
        for entry in f_list:
            menu_list.append((entry[0], entry[1], entry[2], entry[3]))
        #print menu_list
        try:
          self["menu"].UpdateList(menu_list)
        except:
          print "Update asser error :(" #workarround to have it working on openpliPC
          myIndex=self["menu"].getIndex() #as an effect, index is cleared so we need to store it first
          self["menu"].setList(menu_list)
          self["menu"].setIndex(myIndex) #and restore
        self.selectionChanged()
        
    def getInfo(self, f):#currLang
        info = f.replace(".xml", ".txt")
        if path.exists(self.skin_base_dir + "allInfos/info_" + currLang + "_" + info):
            myInfoFile=self.skin_base_dir + "allInfos/info_" + currLang + "_" + info
        elif path.exists(self.skin_base_dir + "allInfos/info_en_" + info):
            myInfoFile=self.skin_base_dir + "allInfos/info_en_" + info
        else:
            #return 'No Info'
            return ''
        
        #with open("/proc/sys/vm/drop_caches", "w") as f: f.write("1\n")
        info = open(myInfoFile, 'r').read().strip()
        return info
            
    def setPicture(self, f):
        pic = f[:-4]
        if path.exists(self.skin_base_dir + "allPreviews/preview_" + pic + '.png'):
            self.UpdatePreviewPicture(self.skin_base_dir + "allPreviews/preview_" + pic + '.png')
        elif path.exists(self.skin_base_dir + "allPreviews/preview_" + pic + '.jpg'):
            self.UpdatePreviewPicture(self.skin_base_dir + "allPreviews/preview_" + pic + '.jpg')
        elif path.exists(self.skin_base_dir + "allPreviews/" + pic + '.png'):
            self.UpdatePreviewPicture(self.skin_base_dir + "allPreviews/" + pic + '.png')
        elif path.exists(self.skin_base_dir + "allPreviews/" + pic + '.jpg'):
            self.UpdatePreviewPicture(self.skin_base_dir + "allPreviews/" + pic + '.jpg')
        else:
            self["PreviewPicture"].hide()
    
    def UpdatePreviewPicture(self, PreviewFileName):
            self["PreviewPicture"].instance.setScale(1)
            self["PreviewPicture"].instance.setPixmap(LoadPixmap(path=PreviewFileName))
            self["PreviewPicture"].show()

    def keyCancel(self):
        self.close()

    def runMenuEntry(self):
        sel = self["menu"].getCurrent()
        if sel[3] == self.enabled_pic:
            remove(self.skin_base_dir + self.file_dir + "/" + sel[0])
        elif sel[3] == self.disabled_pic:
            symlink(self.skin_base_dir + self.allScreens_dir + "/" + sel[0], self.skin_base_dir + self.file_dir + "/" + sel[0])
        self.createMenuList()

    def keyGreen(self):
        if self.EditScreen == True:
            from editscreens import AtileHDEditScreens
            self.session.openWithCallback(self.createMenuList,AtileHDEditScreens, ScreenFile = self.skin_base_dir + self.allScreens_dir + "/" + self["menu"].getCurrent()[0])
        else:
            print "Nothing to Edit :("
            
    def keyYellow(self):
        if self.DeleteScreen == True:
            self.session.openWithCallback(self.keyYellowRet, MessageBox, _("Are you sure you want delete the screen?"), MessageBox.TYPE_YESNO, default = False)
        else:
            print "Nothing to Delete ;)"
    def keyYellowRet(self, result):
        if result is None or result is False:
            printDEBUG("Deletion cancelled.")
        else:
            sel = self["menu"].getCurrent()
            remove((self.skin_base_dir + self.allScreens_dir + "/" + sel[0]))
            pic = sel[0].replace(".xml", ".png")
            if path.exists(self.skin_base_dir + "allPreviews/preview_" + pic):
                remove(self.skin_base_dir + "allPreviews/preview_" + pic)
            self.createMenuList()
