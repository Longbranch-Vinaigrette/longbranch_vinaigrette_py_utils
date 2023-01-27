import os

from ..data_configuration import LocalData


def capture_pid():
    """Capture pid of this app when it's run"""
    LocalData.save_data({
        "pid": os.getpid(),
    })
    with open("pid", "w") as f:
        f.write(f"{os.getpid()}\n")


def remove_pid():
    LocalData.save_data({
        "pid": "",
    })
    os.remove("./pid")
