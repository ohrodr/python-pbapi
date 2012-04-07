
class PinboardAPI():
    def __init__(self):
        self._api_url       = 'https://api.pinboard.in/v1'
        self._handler_realm = 'API'
        self._handler_uri   = 'https://api.pinboard.in/'
        self.useragent      = "libPbAPI/0.1 +http://odr.me/python-pbapi"

    def __setup(self,username,password):
        auth_handler =  urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password( self._handler_realm, \
                                   self._api_url, \
                                   username, password )
        self.opener = urllib2.build_opener(auth_handler)
        self.opener.addheaders = [("User-agent", self.useragent), ('Accept-encoding', 'gzip')]

    def install(self,username,password):
        self.__setup(username,password)
        try:
            urllib2.install_opener(self.opener)
        except:
            raise
