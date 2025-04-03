import csv

import psutil
import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from dataclasses import asdict
from dacite import from_dict

from monitor.models import KillRequest, Snapshot, ProcessData
from monitor.utils import get_processes, parse_sort_param
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

    sort_field, reverse_sort = parse_sort_param(request)

    return render(
        request,
        template_name,
        {
            "processes": sorted(
                get_processes(search, status),
                key=lambda p: getattr(p, sort_field) or 0,
                reverse=reverse_sort,
            ),
            "generated_at": timezone.now(),
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

    return render(
        request, "monitor/kill_notification.html", {"kill_request": None}, status=500
    )


@login_required
@require_GET
def kill_log(request: HtmxHttpRequest):
    return render(
        request,
        "monitor/kill_log.html",
        {"kill_requests": KillRequest.objects.all().order_by("-created_at")},
    )


@login_required
@require_POST
def snapshot(request: HtmxHttpRequest):
    try:
        processes = get_processes(search="", status="")
        snap = Snapshot.objects.create(
            user=request.user, data=[asdict(process) for process in processes]
        )
        return render(request, "monitor/snapshot_notification.html", {"snapshot": snap})
    except Exception as e:
        logger.error(f"Error creating snapshot: {str(e)}")
        return render(
            request,
            "monitor/snapshot_notification.html",
            {"snapshot": None},
            status=500,
        )


@login_required
@require_GET
def snapshot_list(request: HtmxHttpRequest):
    return render(
        request,
        "monitor/snapshots.html",
        {"snapshots": Snapshot.objects.all().order_by("-created_at")},
    )


@login_required
@require_GET
def snapshot_detail(request: HtmxHttpRequest, pk: int = None):
    snap = get_object_or_404(Snapshot, pk=pk)
    processes = [from_dict(ProcessData, process) for process in snap.data]
    return render(
        request,
        "monitor/snapshot_view.html",
        {"processes": processes, "snapshot": snap, "generated_at": snap.created_at},
    )


@login_required
@require_GET
def export_snapshot(request: HtmxHttpRequest, pk: int = None):
    snap = get_object_or_404(Snapshot, pk=pk)
    processes = [from_dict(ProcessData, process) for process in snap.data]
    response = HttpResponse(content_type="text/csv")
    file_name = f"snapshot-{snap.created_at.strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    response["Content-Disposition"] = f"attachment; filename={file_name}"
    writer = csv.writer(response)
    writer.writerow(["PID", "Name", "User", "Status", "Start Time", "CPU", "Memory"])
    for process in processes:
        writer.writerow(
            [
                process.pid,
                process.name,
                process.user,
                process.status,
                process.start_time,
                process.cpu,
                process.memory,
            ]
        )
    return response
