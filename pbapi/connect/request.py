
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
        while self._last and (self._time() - self._last) < 2:
            self._sleep(1)
            self._last = self._time()
        
    def seturl(self,url):
        self.url = url

    def add_to_post(self,kvt):
        """ 
            takes a given key  value tuple
                ( 'foo','bar' ) 
            and assigns that to the self.post_data for this request
        """
        (k,v) = kvt
        self.post_data[k] = v
        
    def _request(self):
        import urllib2
        import StringIO
        import gzip
        import simplejson
        # Make sure that it has been at least 1 second since the last
        # request was made. If not, halt execution for approximately one
        # seconds.
        self._verify_request()

        try:
            ## for pinboard a gzip request is made
            raw_json = urllib2.urlopen(self.url,post_data)
            compresseddata = raw_json.read()
            print compresseddata
            ## bing unpackaging gzipped stream buffer
            compressedstream = StringIO.StringIO(compresseddata)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            self.data = simplejson.load(gzipper)

        except urllib2.URLError, e:
                raise e

        for header in raw_json.headers.headers:
            (name, value) = header.split(": ")
            self.headers[name.lower()] = value[:-2]
        if raw_json.headers.status == "503":
            raise ThrottleError(url, \
                    "503 HTTP status code returned by pinboard.in")
