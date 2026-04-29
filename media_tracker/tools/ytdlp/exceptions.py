class YTDLPUpdateError(Exception):
    pass


class YTDLPUpdateAlreadyRunningError(YTDLPUpdateError):
    pass


class YTDLPAlreadyUpToDateError(YTDLPUpdateError):
    pass