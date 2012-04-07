class Request():
    def __init__(self):
        import time
        self._time = time.time
        self._sleep = time.sleep
        self._last = self._time()


    def _verify_request(self):
        while self._last and (self._time() - self._last) < 2:
            self._sleep(1)
            self._last = self._time()
        
    def _request(self, url):

        # Make sure that it has been at least 1 second since the last
        # request was made. If not, halt execution for approximately one
        # seconds.
        if self.__lastrequest and (time.time() - self.__lastrequest) < 2:
            if _debug:
                sys.stderr.write("It has been less than two seconds since the last request; halting execution for one second.\n")
            time.sleep(1)
        if _debug and self.__lastrequest:
            sys.stderr.write("The delay between requests was %d.\n" % (time.time() - self.__lastrequest))
        self.__lastrequest = time.time()
        if _debug:
            sys.stderr.write("Opening %s.\n" % url)

        try:
            ## for pinboard a gzip request is made
            raw_xml = urllib2.urlopen(url)
            compresseddata = raw_xml.read()
            ## bing unpackaging gzipped stream buffer
            compressedstream = StringIO.StringIO(compresseddata)
            gzipper = gzip.GzipFile(fileobj=compressedstream)
            xml = gzipper.read()

        except urllib2.URLError, e:
                raise e

        self["headers"] = {}
        for header in raw_xml.headers.headers:
            (name, value) = header.split(": ")
            self["headers"][name.lower()] = value[:-2]
        if raw_xml.headers.status == "503":
            raise ThrottleError(url, \
                    "503 HTTP status code returned by pinboard.in")
        if _debug:
            sys.stderr.write("%s opened successfully.\n" % url)
        return minidom.parseString(xml)

