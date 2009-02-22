from libsheep.state import State

class API(object):
    def __init__(self):
        self.state = State()

    def search_send(self,hub,search,timeout):
        pass

    def get_list(self,hub,user):
        pass

    def set_options(self,option,value):
        pass

    def lib_connect(self):
        pass

    def connect(self,hub):
        pass

    def lib_disconnect(self,state):
        pass

    def disconnect(self,hub):
        pass

    def rehash(self):
        pass

    def info_update(self):
        pass

    def send_chat(self,hub,chat):
        pass

    def send_pm(self,user,chat):
        pass

    def recv_chat(self):
        pass

    def recv_pm(self):
        pass

    def status_update(self):
        pass

    def transfer_update(self):
        pass

    def add_to_list(self,path):
        self.state.file_list.add(path)
        return

    def remove_from_list(self,path):
        self.state.file_list.remove(path)
        return

    def download(self,file_tok):
        pass
