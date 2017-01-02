#!/usr/bin/python3

# A python3 port of musicctl.sh.

import os
import sys
import player


# warning() functions like print, except it prefixes everything and prints to
# stderr.
def warning(*objs, prefix='WARNING: '):
    printed_list = str(prefix)
    for i in objs:
        printed_list += str(i)
    print(printed_list, file=sys.stderr)


def usage(exit_code, name):
    usage_text = "Usage: %s {[a command]|player|commands|usage|help}" % name

    if exit_code == 0:
        print(usage_text)
    elif exit_code > 0:
        warning(usage_text, prefix='')
    elif exit_code < 0:
        usage(exit_code, name)
    exit(exit_code)


def processargs(input_argv):

    # All of these run in the same scope as processargs(). They make changes to
    # output.
    def _help():
        usage(0, output['name'])

    def _trial():
        output["test_mode_prefix"] = 'echo '
        output["test_mode_suffix"] = ''

    def _player():
        if '=' in input_argv[i]:
            player = input_argv[i].split('=')[1]
        else:
            player = input_argv[i + 1]
            indexes_to_ignore.append(i + 1)
        try:
            output["player"] = {
                'mpd': player.mpd,
                'mpc': player.mpd,
                'pianobar': player.pianobar,
                'pianoctl': player.pianobar,
                'playerctl': player.playerctl,
                'mpris': player.playerctl,
                }[player]()
        except KeyError:
            warning('Invalid player')
            exit(1)

    # In place of a switch-case statement the following dictionaires link argv
    # entries to functions.
    long_args_to_disc = {'--help': _help,
                         '--trial': _trial, '--player': _player}
    short_args_to_disc = {'h': _help, 't': _trial, 'p': _player}
    output = {"input": None,
              "test_mode_prefix": '',
              "test_mode_suffix": ' >/dev/null',
              "name": os.path.basename(input_argv[0]),
              "player": None,
              }
    indexes_to_ignore = list()

    if len(input_argv) == 1:
        warning("Not enough arguments")
        usage(1, output['name'])
    else:
        # range() starts at 1 to prevent the name from being processed.
        for i in range(1, len(input_argv)):
            if i in indexes_to_ignore:
                continue

            elif len(input_argv[i]) >= 2 and input_argv[i][0:2] == '--':
                try:
                    long_args_to_disc[input_argv[i].split('=')[0]]()
                except KeyError:
                    warning("Invalid argument", prefix='')
                    usage(1, output['name'])

            elif input_argv[i][0] == '-' and input_argv[i][1] != '-':
                for j in range(1, len(input_argv[i])):
                    try:
                        short_args_to_disc[input_argv[i][j]]()
                    except KeyError:
                        warning("Invalid argument", prefix='')
                        usage(1, output['name'])

            elif output["input"] is None:
                output["input"] = input_argv[i]

            else:
                warning("Error parsing arguments")
                usage(1, output['name'])

    return output


# global arguments
arguments = processargs(sys.argv)


def main(arguments):
    # Handle help and usage correctly:
    if arguments["input"] == "usage" or arguments["input"] == "help":
        usage(0, arguments['name'])

    if arguments["input"] == "commands":
        player.print_keys()
        exit(0)

    # Figure out what player is running.
    if arguments['player'] is not None:
        current_player = arguments['player']
    else:
        current_player = player.current_player()
    if arguments["input"] == "player":
        print(current_player)
        exit(0)

    # Catching a KeyError should prevent this from exploding over the user
    # giving invalid input.
    try:
        current_player.commands[arguments["input"]]()
    except KeyError:
        warning("Invalid input.")
        usage(1, arguments['name'])


if __name__ == "__main__":
    main(arguments)
