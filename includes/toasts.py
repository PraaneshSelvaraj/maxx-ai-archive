from win11toast import toast

class Toasts():
    def new_connection(self, device):
        resp = toast(f"New Connection : {device}", "Do you want to connect?", buttons=['Yes', 'No'])
        if resp['arguments'] == 'http:Yes':
            return True
        
        return False