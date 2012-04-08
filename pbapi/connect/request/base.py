class Request():
    def __init__(self):
        import time
        self._time = time.time
        self._sleep = time.sleep
        self._last = self._time()
        self.headers = {}
        self.data = None 
        self.post_data = { 'format':'json' }
        self.url = ''


    def _verify_request(self):
        while (self._time() - self._last) < 2:
            self._sleep(1)
            self._last = self._time()
        
    def seturl(self,url):
        self.url = url

    def add_parm(self,kvt):
        """ 
            takes a given key  value tuple
                ( 'foo','bar' ) 
            and assigns that to the self.post_data for this request
        """
        (k,v) = kvt
        self.post_data[k] = v
        
    def _unzip(self,compressed_data):
        import StringIO
        import gzip
        compress_stream = StringIO.StringIO(compressed_data)
        gzip_file = gzip.GzipFile(fileobj=compress_stream)
        data = []
        for line in gzip_file.readlines(): yield line

    def _post_to_get(self,parms_encoded):
        from urllib import urlencode
        """
           Currently there are only GET methods supported.
           I wrote on the assumption there would be POST support.
           I have included this method as an interim until POST is supported.
           input: urlencoded dict
           output string containing full_http_get_uri 
        """
        full_uri = '?'.join([self.url,urlencode(self.post_data)])
        print full_uri
        return full_uri 

    def _request(self):
        import urllib2
        import urllib
        # Make sure that it has been at least 1 second since the last
        # request was made. If not, halt execution for approximately one
        # seconds.
        #self._verify_request()

        try:
            ## for pinboard a gzip request is made
            encode_parms = urllib.urlencode(self.post_data)
            raw_response = urllib2.urlopen(self._post_to_get(encode_parms))
            self.data = self._unzip(raw_response.read())

        except urllib2.URLError, e:
                raise e

        if raw_response.headers.status == "503":
            raise pbapi.pbexcept.ThrottleError(url, \
                    "503 HTTP status code returned by pinboard.in")
