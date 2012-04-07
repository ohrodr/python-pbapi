
class PinboardAPI():
    def __init__(self):
        self._api_url       = 'https://api.pinboard.in/v1'
        self._handler_realm = 'API'
        self._handler_uri   = 'https://api.pinboard.in/'
        self.useragent      = "libPbAPI/0.1 +http://odr.me/python-pbapi"

    def _setup(self,username,pass_word):
        import urllib2
        """
            This is meant to be a private method.  There should be no need to call this specifically.
            Inputs are 2 variables, username and pass_word
            The return is void, and basically sets the object up with the appropriate handler and opener.
        """
        auth_handler =  urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password( self._handler_realm, \
                                   self._api_url, \
                                   username, pass_word )
        self.opener = urllib2.build_opener(auth_handler)
        self.opener.addheaders = [("User-agent", self.useragent), ('Accept-encoding', 'gzip')]

    def install(self,username,pass_word):
        """ Primary method for creating the API handler. """
        import urllib2
        self._setup(username,pass_word)
        try:
            urllib2.install_opener(self.opener)
        except:
            raise
