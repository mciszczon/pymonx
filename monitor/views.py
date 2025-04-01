import psutil
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET

from monitor.models import KillRequest
from monitor.utils import get_processes
from pymonx.utils import HtmxHttpRequest


logger = logging.getLogger(__name__)


@login_required
@require_GET
def index(request: HtmxHttpRequest):
    search = request.GET.get("search", "")
    status = request.GET.get("status", "")

    template_name = "monitor/index.html"
    if request.htmx:
        template_name += "#process-table"

    return render(
        request,
        template_name,
        {
            "processes": sorted(
                get_processes(search, status),
                key=lambda p: p["start_time"],
                reverse=True,
            )
        },
    )


@login_required
@require_POST
def kill(request: HtmxHttpRequest):
    pid = int(request.POST.get("pid"))
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        kill_request = KillRequest.objects.create(
            pid=pid,
            name=process_name,
            user=request.user,
        )
        process.terminate()
        kill_request.success = True
        kill_request.save(update_fields=["success"])
        return render(
            request, "monitor/kill_notification.html", {"kill_request": kill_request}
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    except Exception as e:
        logger.error(f"Error killing process: {str(e)}")

    return render(request, "monitor/kill_notification.html", {"kill_request": None})


@login_required
@require_GET
def kill_log(request: HtmxHttpRequest):
    return render(
        request,
        "monitor/kill_log.html",
        {"kill_requests": KillRequest.objects.all().order_by("-created_at")},
    )
