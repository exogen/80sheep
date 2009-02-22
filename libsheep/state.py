from libsheep.filelist import FileListing

class State(object):
    def __init__(self):
        self.file_list = FileListing(None)
        self.downloaded_lists = None
        self.hubs = None
