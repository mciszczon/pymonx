from datetime import datetime


def bytes_to_mib(bytes_size: int) -> float:
    return bytes_size / (1024**2)


def time_since(timestamp: int) -> str:
    now = datetime.now()
    delta = now - datetime.fromtimestamp(timestamp)

    days = delta.days
    seconds = delta.seconds
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:  # Always show at least seconds
        parts.append(f"{seconds}s")

    return " ".join(parts)
