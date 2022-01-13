from datetime import datetime
from app.logger import log


def get_status():
    """[Get last 10 strings of logs]

    Returns:
        [List]: [Strings of logs]
    """
    today = datetime.today()
    if len(str(today.day)) == 1:
        day = f"0{today.day}"
    else:
        day = today.day
    if len(str(today.month)) == 1:
        month = f"0{today.month}"
    else:
        month = today.day
    path = f"/tmp/update-all-vida-{today.year}-{month}-{day}.log"
    with open(path, "r") as file:
        full_line = ""
        for line in file.readlines()[-11:-1]:
            full_line += line
        log(log.INFO, "Status: %s", full_line)
        if not full_line:
            full_line = "Log file is empty"
        return full_line
