#!/usr/bin/python3

from os import listdir as _listdir
from os.path import join as _join
from typing import List, Dict


__all__ = [
    "is_comm_running",
    "get_comms_to_pids",
    "get_pids_to_comms",
    "get_pids_to_cmdlines",
    "get_pids_of_comm",
    "get_comm_of_pid",
    "get_pids",
    "get_comms",
    "get_pids_of_comm",
    "update_buffers",
    "get_cmdline_of_pid",
]

_buffer_map_pids_to_comms = {}  # type: Dict[str, str]
_buffer_map_pids_to_cmdlines = {}  # type: Dict[str, List[str]]
_buffer_map_comms_to_pids = {}  # type: Dict[str, List[str]]
_buffer_running_pids = []  # type: List[str]
_buffer_list_of_comms = []  # type: List[str]


def _build_buffers() -> None:
    global _buffer_map_pids_to_comms
    global _buffer_map_pids_to_cmdlines
    global _buffer_running_pids
    global _buffer_list_of_comms
    global _buffer_map_comms_to_pids
    global _buffer_map_comms_to_pids

    _buffer_map_pids_to_comms = {}  # Dict[str, str]
    _buffer_map_pids_to_cmdlines = {}  # Dict[str, List[str]]
    _buffer_running_pids = [pid for pid in _listdir('/proc') if pid.isdigit()]
    _buffer_list_of_comms = []  # List[str]
    _buffer_map_comms_to_pids = {}  # type: Dict[str, List[str]]

    for index, pid in enumerate(_buffer_running_pids):
        try:
            comm_file = open(_join('/proc', pid, 'comm'), 'r')
            comm = comm_file.read().rstrip('\n')
            comm_file.close()
            _buffer_map_pids_to_comms[pid] = comm

            cmd_file = open(_join('/proc', pid, 'cmdline'), 'r')
            cmd = cmd_file.read().rstrip('\n')
            cmd_file.close()
            cmdline = cmd.split('\x00')

            _buffer_map_pids_to_cmdlines[pid] = cmdline

            if comm not in _buffer_list_of_comms:
                _buffer_list_of_comms.append(comm)
                _buffer_map_comms_to_pids[comm] = list()

            _buffer_map_comms_to_pids[comm].append(pid)

        except FileNotFoundError:
            _buffer_running_pids.pop(index)


def update_buffers() -> None:
    _build_buffers()


def get_pids() -> List[str]:
    """Returns a list of pids"""
    return _buffer_running_pids


def get_comms() -> List[str]:
    """Returns a list of comms"""
    return _buffer_list_of_comms


def get_comms_to_pids() -> Dict[str, List[str]]:
    """Returns a dict of comms as keys and a list of pids as values"""
    return _buffer_map_comms_to_pids


def get_pids_to_comms() -> Dict[str, str]:
    """Returns a dict of pids as keys and a string of the comm as values"""
    return _buffer_map_pids_to_comms


def get_pids_of_comm(comm: str) -> List[str]:
    """Returns a list of all pids with comm"""
    try:
        pids = _buffer_map_comms_to_pids[comm]
    except KeyError:
        pids = []
    return pids


def get_pids_to_cmdlines() -> Dict[str, List[str]]:
    """Returns a dict of pids as keys and a string of the comm as values"""
    return _buffer_map_pids_to_cmdlines


def get_comm_of_pid(pid: str) -> str:
    """Returns the str of the comm of a pid"""
    return _buffer_map_pids_to_comms[pid]


def get_cmdline_of_pid(pid: str) -> List[str]:
    """Returns the list with each argv entry of pid as a different string"""
    return _buffer_map_pids_to_cmdlines[pid]


def is_comm_running(comm: str) -> bool:
    """Returns a bool if any process with that comm is running"""
    return comm in _buffer_list_of_comms


_build_buffers()
