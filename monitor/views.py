import logging

import psutil

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from monitor.utils import bytes_to_mib
from pymonx.utils import HtmxHttpRequest

# Get an instance of a logger
logger = logging.getLogger(__name__)


@login_required
def index(request: HtmxHttpRequest):
    processes = []

    for process in psutil.process_iter(
        [
            "pid",
            "name",
            "username",
            "status",
            "create_time",
            "cpu_percent",
            "memory_info",
        ]
    ):
        if process.info["pid"] == 0:
            continue
        if process.info["username"] == "root":
            continue
        try:
            processes.append(
                {
                    "pid": process.info["pid"],
                    "name": process.info["name"],
                    "user": process.info["username"] or "unknown",
                    "status": process.info["status"],
                    "start_time": process.info["create_time"],
                    "cpu": process.info["cpu_percent"],
                    "memory": "{:.2f}".format(
                        bytes_to_mib(process.info["memory_info"].rss)
                    )
                    if process.info["memory_info"]
                    else None,
                }
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    template_name = "monitor/index.html"
    if request.htmx:
        template_name += "#process-table"

    return render(request, template_name, {"processes": reversed(processes)})
