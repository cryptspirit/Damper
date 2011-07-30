#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
#       damper.py
#       
#       Copyright 2011 CryptSpirit <cryptspirit@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
import gtk
import gobject
import subprocess
import sys
import time
import re
import pygtk
import string

pygtk.require('2.0')
from threading import Timer

channel = 'Master'
exit_flag = True
audio_volume_muted = gtk.icon_theme_get_default().load_icon('audio-volume-muted', 22, gtk.ICON_LOOKUP_USE_BUILTIN)
audio_volume_high = gtk.icon_theme_get_default().load_icon('audio-volume-high', 22, gtk.ICON_LOOKUP_USE_BUILTIN)


def get_amixer(card_number):
    ret_dict = {}
    value_key = ''
    s = subprocess.Popen(['amixer', '-c', str(card_number)], stdout=subprocess.PIPE).communicate()[0]
    for i in s.split('\n'):
        tmp = (i.strip(' ')).split(':')
        if string.count(tmp[0], 'Simple mixer control'):
            p = re.search(r'\'.*\'', tmp[0]).group()
            value_key = p[1:-1]
            ret_dict[value_key] = {}
        else:
            try: ret_dict[value_key][tmp[0].strip(' ')] = tmp[1].strip(' ')
            except: pass
    return ret_dict
            
def get_mute():
    while exit_flag:
        s = subprocess.Popen(['amixer', '-c', '0', 'get', 'Master'], stdout=subprocess.PIPE).communicate()[0]
        try: re.search(r"\[off\]", s).group()
        except:
            if_mut(False)
        else:
            if_mut(True)
        time.sleep(2)

def if_mut(mut):
    global win
    if win.cheak.get_active != mut:
        gtk.gdk.threads_enter()
        win.cheak.set_active(mut)
        gtk.gdk.threads_leave()
        if mut:
            gtk.gdk.threads_enter()
            win.icon.set_from_pixbuf(audio_volume_muted)
            gtk.gdk.threads_leave()
        else:
            gtk.gdk.threads_enter()
            win.icon.set_from_pixbuf(audio_volume_high)
            gtk.gdk.threads_leave()

class window_conf(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_position(gtk.WIN_POS_CENTER)
        self.show

class windows_vol(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.icon = gtk.status_icon_new_from_pixbuf(audio_volume_high)
        self.icon.connect('activate', self.show_win)
        self.icon.connect('popup-menu', self.menu)
        self.set_default_size(25, 200)
        self.set_decorated(False)
        self.connect('focus-out-event', self.focus_lost)
        self.scale_vol_control = gtk.VScale()
        self.scale_vol_control.set_digits(0)
        self.scale_vol_control.set_inverted(True)
        self.scale_vol_control.connect('format-value', self.Sound_Control)
        self.cheak = gtk.CheckButton(None)
        self.cheak.connect('toggled', self.toggled_mut)
        self.bo = gtk.VBox()
        self.bo.pack_start(self.scale_vol_control, True, True, 0)
        self.bo.pack_start(self.cheak, False, False, 0)
        self.add(self.bo)
        
    def toggled_mut(self, *args):
        if self.cheak.get_active():
            subprocess.Popen(['amixer', '-c', '0', 'set', 'Master', 'mute'], stdout=None)
        else:
            subprocess.Popen(['amixer', '-c', '0', 'set', 'Master', 'unmute'], stdout=None)
        self.if_mut(self.cheak.get_active())
        
    def if_mut(self, mut):
        if self.cheak.get_active != mut:
            self.cheak.set_active(mut)
            if mut:
                self.icon.set_from_pixbuf(audio_volume_muted)
            else:
                self.icon.set_from_pixbuf(audio_volume_high)
            
             
    def menu(self, icon, event_button, event_time):
        menu = gtk.Menu()
        item = gtk.MenuItem('Exit')
        item.connect('activate', self.dest)
        item.show()
        item1 = gtk.MenuItem('Config')
        item1.connect('activate', self.show_conf)
        item1.show()
        menu.append(item)
        menu.append(item1)
        menu.popup(None, None, gtk.status_icon_position_menu, event_button, event_time, icon)
            
    def focus_lost(self, *args):
        args[0].hide()
            
    def show_conf(self, *args):
        h = window_conf()
        h.show()
        
    def show_win(self, *args):
        max, min, val = self.getval(channel)
        self.scale_vol_control.set_range(min, max)
        self.scale_vol_control.set_value(val)
        self.set_position(gtk.WIN_POS_MOUSE)
        self.show_all()
        
    def dest(self, *args):
        global exit_flag
        self.icon.set_visible(False)
        gtk.main_quit()
        exit_flag = False
        sys.exit(0)
        
    def getval(self, chl):
        s = subprocess.Popen(['amixer', '-c', '0', 'get', channel], stdout=subprocess.PIPE).communicate()[0]
        s1 = re.search(r"Front Left: .* \[", s).group()[21:-1]

        val = re.search(r".*\d \[", s1).group()[:-2]
        s2 = re.search(r"Limits: Playback .*", s).group()[17:]
        minn = re.search(r".* -", s2).group()[:-2]
        return int(s2[len(minn) + 2:]), int(minn), int(val)
        
    def Sound_Control(self, *args):
            subprocess.Popen(['amixer', '-c', '0', 'set', channel, str(args[0].get_value())], stdout=None)

gobject.type_register(windows_vol)
        
def main():
    print get_amixer(0)
    global win
    gtk.gdk.threads_init()
    win = windows_vol()
    tim = Timer(0, get_mute)
    tim.start()
    gtk.main()
    return 0

if __name__ == '__main__':
    main()

