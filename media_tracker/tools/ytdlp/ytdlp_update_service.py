from media_tracker.models.ytdlp import YTDLPUpdateResult

from media_tracker.tools.ytdlp.exceptions import (
    YTDLPUpdateAlreadyRunningError,
    YTDLPAlreadyUpToDateError
)

from media_tracker.tools.ytdlp.ytdlp_management import (
    get_installed_version,
    get_latest_release,
    download_latest_binary,
    replace_binary
)

from media_tracker.tools.ytdlp.ytdlp_state import (
    update_lock,
    update_state
)


def update_ytdlp() -> YTDLPUpdateResult:

    if not update_lock.acquire(blocking=False):
        raise YTDLPUpdateAlreadyRunningError(
            "yt-dlp update already in progress"
        )

    update_state.updating = True
    update_state.last_error = None

    try:

        installed_version = get_installed_version()

        release = get_latest_release()

        latest_version = release["tag_name"]

        if installed_version == latest_version:
            raise YTDLPAlreadyUpToDateError(
                "yt-dlp is already up to date"
            )

        asset = next(
            asset
            for asset in release["assets"]
            if asset["name"] == "yt-dlp_linux"
        )

        download_latest_binary(
            asset["browser_download_url"]
        )

        replace_binary()

        return YTDLPUpdateResult(
            old_version=installed_version,
            new_version=latest_version,
            updated=True
        )

    except Exception as e:

        update_state.last_error = str(e)

        raise

    finally:

        update_state.updating = False
        update_lock.release()