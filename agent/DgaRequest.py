from datetime import datetime


class DgaRequest:
    class __DgaRequest:
        def __init__(self, cookie, csrf_token):
            self.cookie = cookie
            self.csrf_token = csrf_token
            self.date = datetime.utcnow()

        def __str__(self):
            return repr(self) + self.cookie + self.csrf_token + self.date

        def checkDate(self):
            renew = False
            if datetime.utcnow().minute - self.date.minute >= 3:
                    renew = True

            return renew

        def getCookie(self):
            return self.cookie

        def getToken(self):
            return self.csrf_token

    instance = None

    def __init__(self, cookie, csrf_token):
        if not DgaRequest.instance:
            DgaRequest.instance = DgaRequest.__DgaRequest(cookie, csrf_token)
        else:
            DgaRequest.instance.cookie = cookie
            DgaRequest.instance.csrf_token = csrf_token

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def setCookie(self, cookie):
        DgaRequest.instance.cookie = cookie

    def setToken(self, token):
        DgaRequest.instance.csrf_token = token
