from datetime import datetime


def log(message):
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[Energy Hub] {timestamp} | {message}",
        flush=True,
    )