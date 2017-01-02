#!/usr/bin/python3

# A python3 port of musicctl.sh.

import time
import os
import sys
import re
import subprocess
import process


# warning() functions like print, except it prefixes everything and prints to
# stderr.
def warning(*objs, prefix='WARNING: '):
    printed_list = str(prefix)
    for i in objs:
        printed_list += str(i)
    print(printed_list, file=sys.stderr)


def get_keys(list_of_classes):
    for i in list_of_classes:
        print("For player " + str(i) +
              " the following commands are available:")
        for j in sorted(i.commands.keys()):
            print("   " + j)

    exit(0)


class mpd:
    __name__ = 'mpd'

    def __init__(self):
        self.commands = {'play': self.pause, 'pause': self.pause,
                         'back': self.back, 'next': self.next,
                         'quit': self.stop, 'stop': self.stop,
                         'is_playing': self.is_playing_shell_wrapper}

    def _call_mpc(self, *option):
        devnull = open('/dev/null')
        subprocess.call(['mpc', *option], stdout=devnull.buffer)
        devnull.close()

    def __repr__(self):
        return self.__name__

    def pause(self):
        self._call_mpc('toggle')

    def back(self):
        self._call_mpc('prev')

    def next(self):
        self._call_mpc('next')

    def stop(self):
        self._call_mpc('stop')

    def is_playing_shell_wrapper(self):
        if self.is_playing():
            exit(0)
        else:
            exit(1)

    def is_playing(self):
        try:
            is_playing_present = b"playing" in subprocess.check_output(
                ['mpc', 'status'])
        except subprocess.CalledProcessError:
            is_playing_present = False
        return is_playing_present


# Since the easiest way to control mopidy is through its mpd implementation,
# the mopidy class inherets its implementation from the mpd class.
class mopidy(mpd):
    __name__ = 'mopidy'


class pianobar:
    __name__ = 'pianobar'

    def __init__(self):
        self.commands = {'play': self.pause, 'pause': self.pause,
                         'back': self.like, 'next': self.next,
                         'quit': self.stop, 'stop': self.stop,
                         'tired': self.tired, 'like': self.like,
                         'dislike': self.dislike,
                         'is_playing': self.is_playing_shell_wrapper}

    def __repr__(self):
        return self.__name__

    def _call_pianoctl(self, option):
        subprocess.call(
            ['pianoctl', option])

    def pause(self):
        self._call_pianoctl('p')

    def like(self):
        self._call_pianoctl('+')

    def dislike(self):
        self._call_pianoctl('-')

    def next(self):
        self._call_pianoctl('n')

    def stop(self):
        self._call_pianoctl('q')
        # if pianobar isn't responding kill it.
        time.sleep(1)
        process.update_buffers()
        if process.is_comm_running("pianobar"):
            subprocess.call(['kill'] + process.get_pids_of_comm('pianobar'))

    def tired(self):
        self._call_pianoctl('t')

    def is_playing_shell_wrapper(self):
        if self.is_playing():
            exit(0)
        else:
            exit(1)

    def is_playing(self):
        log1_time_stamp, success1 = self._get_time()
        time.sleep(2)
        log2_time_stamp, success2 = self._get_time()

        if not (success1 and success2):
            output = False
        if log1_time_stamp == log2_time_stamp:
            output = False
        else:
            output = True
        return output

    def _get_time(self, tries=0):
        """Reads the pianobar time, and returns a tuple of  str '##:##/##:##'
        and a boolean which reflects whether it matches the regex"""
        log = open(os.path.expanduser('~/.config/pianobar/out'), 'r')
        time_stamp = log.read()[-12:-1]
        log.close()
        if re.match(r'^\d{2}:\d{2}/\d{2}:\d{2}$', time_stamp):
            return (time_stamp, True)
        elif tries < 3:
            time.sleep(1)
            return self._get_time(tries+1)
        else:
            return (time_stamp, False)


class playerctl:
    __name__ = 'playerctl'

    def __init__(self):
        self.commands = {'play': self.pause, 'pause': self.pause,
                         'back': self.back, 'next': self.next,
                         'quit': self.stop, 'stop': self.stop,
                         'is_playing': self.is_playing_shell_wrapper}

    def __repr__(self):
        return self.__name__

    def _call_playerctl(self, option):
        subprocess.call(
            ['playerctl', option])

    def pause(self):
        self._call_playerctl('play-pause')

    def back(self):
        self._call_playerctl('previous')

    def next(self):
        self._call_playerctl('next')

    def stop(self):
        self._call_playerctl('stop')

    def is_playing_shell_wrapper(self):
        if self.is_playing():
            exit(0)
        else:
            exit(1)

    def is_playing(self):
        try:
            is_playing_present = b"Playing" in subprocess.check_output(
                ['playerctl', 'status'])
        except subprocess.CalledProcessError:
            is_playing_present = False
        return is_playing_present


def current_player():
    list_of_process_names = process.get_comms()

    # pianobar get priority over mpd, unless mpd is playing.
    if 'mpd' in list_of_process_names:
        if 'pianobar' in list_of_process_names:
            if b'playing' in subprocess.check_output(['mpc', 'status']):
                output = mpd()
            else:
                output = pianobar()
        else:
            output = mpd()
    elif 'pianobar' in list_of_process_names:
        output = pianobar()
    elif 'mopidy' in list_of_process_names:
        output = mopidy()
    else:
        output = playerctl()

    return output


def is_playing():
    return current_player().is_playing()


def pause():
    current_player().commands['pause']()


def stop():
    current_player().commands['stop']()


def back():
    current_player().commands['back']()


def next_song():
    current_player().commands['next']()


def print_keys(list_of_classes=[mopidy, mpd, pianobar, playerctl]):
    for i in list_of_classes:
        player = i()
        print("For player " + player.__repr__() +
              " the following commands are available:")
        for j in sorted(player.commands.keys()):
            print("   " + j)


if __name__ == '__main__':
    print('Please don\'t do this.')
