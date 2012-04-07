import datetime


class PinboardAccount(dict):
    """A pinboard.in account"""

    # Used to track whether all posts have been downloaded yet.
    __allposts = 0
    __postschanged = 0

    # Time of last request so that the one second limit can be enforced.
    __lastrequest = None

    # Special methods

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self,key)
        except KeyError:
            if key == "tags":
                return self.tags()
            elif key == "dates":
                return self.dates()
            elif key == "posts":
                return self.posts()
            elif key == "bundles":
                return self.bundles()
            else:
                raise pbexcept.PinboardError()

    def __setitem__(self, key, value):
        if key == "posts":
            self.__postschanged = 1
        return dict.__setitem__(self, key, value)


    def __request(self, url):

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




    def posts(self, tag="", date="", todt="", fromdt="", count=0):
        """Return pinboard.in bookmarks as a list of dictionaries.

        This should be used without arguments as rarely as possible by
        combining it with the lastupdate attribute to only get all posts when
        there is new content as it places a large load on the pinboard.in
        servers.

        """
        query = {}

        ## if a date is passed then a ranged set of date params CANNOT be passed
        if date and (todt or fromdt):
            raise DateParamsError

        if not count and not date and not todt and not fromdt and not tag:
            path = "all"

           # If attempting to load all of the posts from pinboard.in, and
            # a previous download has been done, check to see if there has
            # been an update; if not, then just return the posts stored
            # inside the class.
            if _debug:
                sys.stderr.write("Checking to see if a previous download has been made.\n")
            if not self.__postschanged and self.__allposts and \
                    self.lastupdate() == self["lastupdate"]:
                if _debug:
                    sys.stderr.write("It has; returning old posts instead.\n")
                return self["posts"]
            elif not self.__allposts:
                if _debug:
                    sys.stderr.write("Making note of request for all posts.\n")
                self.__allposts = 1
        elif date:
            path = "get"
        elif todt or fromdt:
            path = "all"
        else:
            path = "recent"
        if count:
            query["count"] = count
        if tag:
            query["tag"] = tag

        ##todt
        if todt and (isinstance(todt, ListType) or isinstance(todt, TupleType)):
            query["todt"] = "-".join([str(x) for x in todt[:3]])
        elif todt and (todt and isinstance(todt, datetime.datetime) or \
                isinstance(todt, datetime.date)):
            query["todt"] = "-".join([str(todt.year), str(todt.month), str(todt.day)])
        elif todt:
            query["todt"] = todt

        ## fromdt
        if fromdt and (isinstance(fromdt, ListType) or isinstance(fromdt, TupleType)):
            query["fromdt"] = "-".join([str(x) for x in fromdt[:3]])
        elif fromdt and (fromdt and isinstance(fromdt, datetime.datetime) or \
                isinstance(fromdt, datetime.date)):
            query["fromdt"] = "-".join([str(fromdt.year), str(fromdt.month), str(fromdt.day)])
        elif fromdt:
            query["fromdt"] = fromdt

        if date and (isinstance(date, ListType) or isinstance(date, TupleType)):
            query["dt"] = "-".join([str(x) for x in date[:3]])
        elif date and (datetime and isinstance(date, datetime.datetime) or \
                isinstance(date, datetime.date)):
            query["dt"] = "-".join([str(date.year), str(date.month), str(date.day)])
        elif date:
            query["dt"] = date

        postsxml = self.__request("%s/posts/%s?%s" % (PINBOARD_API, path, \
                urllib.urlencode(query))).getElementsByTagName("post")
        posts = []
        if _debug:
            sys.stderr.write("Parsing posts XML into a list of dictionaries.\n")
        # For each post, extract every attribute (splitting tags into sub-lists)
        # and insert as a dictionary into the `posts` list.
        for post in postsxml:
            postdict = {}
            for (name, value) in post.attributes.items():
                if name == u"tag":
                    name = u"tags"
                    value = value.split(" ")
                if name == u"time":
                    postdict[u"time_parsed"] = time.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                postdict[name] = value
            if self.has_key("posts") and isinstance(self["posts"], ListType) \
                    and postdict not in self["posts"]:
                self["posts"].append(postdict)
            posts.append(postdict)
        if _debug:
            sys.stderr.write("Inserting posts list into class attribute.\n")
        if not self.has_key("posts"):
            self["posts"] = posts
        if _debug:
            sys.stderr.write("Resetting marker so module doesn't think posts has been changed.\n")
        self.__postschanged = 0
        return posts

    def suggest(self, url):
        query = {'url': url}
        tags = self.__request("%s/posts/suggest?%s" % (PINBOARD_API, urllib.urlencode(query)))

        popular = [t.firstChild.data for t in tags.getElementsByTagName('popular')]
        recommended = [t.firstChild.data for t in tags.getElementsByTagName('recommended')]

        return {'popular': popular, 'recommended': recommended}

    def tags(self):
        """Return a dictionary of tags with the number of posts in each one"""
        tagsxml = self.__request("%s/tags/get?" % \
                PINBOARD_API).getElementsByTagName("tag")
        tags = []
        if _debug:
            sys.stderr.write("Parsing tags XML into a list of dictionaries.\n")
        for tag in tagsxml:
            tagdict = {}
            for (name, value) in tag.attributes.items():
                if name == u"tag":
                    name = u"name"
                elif name == u"count":
                    value = int(value)
                tagdict[name] = value
            if self.has_key("tags") and isinstance(self["tags"], ListType) \
                    and tagdict not in self["tags"]:
                self["tags"].append(tagdict)
            tags.append(tagdict)
        if _debug:
            sys.stderr.write("Inserting tags list into class attribute.\n")
        if not self.has_key("tags"):
            self["tags"] = tags
        return tags

    def bundles(self):
        """Return a dictionary of all bundles"""
        bundlesxml = self.__request("%s/tags/bundles/all" % \
                PINBOARD_API).getElementsByTagName("bundle")
        bundles = []
        if _debug:
            sys.stderr.write("Parsing bundles XML into a list of dictionaries.\n")
        for bundle in bundlesxml:
            bundledict = {}
            for (name, value) in bundle.attributes.items():
                bundledict[name] = value
            if self.has_key("bundles") and isinstance(self["bundles"], ListType) \
                    and bundledict not in self["bundles"]:
                self["bundles"].append(bundledict)
            bundles.append(bundledict)
        if _debug:
            sys.stderr.write("Inserting bundles list into class attribute.\n")
        if not self.has_key("bundles"):
            self["bundles"] = bundles
        return bundles

    def dates(self, tag=""):
        """Return a dictionary of dates with the number of posts at each date"""
        if tag:
            query = urllib.urlencode({"tag":tag})
        else:
            query = ""
        datesxml = self.__request("%s/posts/dates?%s" % \
                (PINBOARD_API, query)).getElementsByTagName("date")
        dates = []
        if _debug:
            sys.stderr.write("Parsing dates XML into a list of dictionaries.\n")
        for date in datesxml:
            datedict = {}
            for (name, value) in date.attributes.items():
                if name == u"date":
                    datedict[u"date_parsed"] = time.strptime(value, "%Y-%m-%d")
                elif name == u"count":
                    value = int(value)
                datedict[name] = value
            if self.has_key("dates") and isinstance(self["dates"], ListType) \
                    and datedict not in self["dates"]:
                self["dates"].append(datedict)
            dates.append(datedict)
        if _debug:
            sys.stderr.write("Inserting dates list into class attribute.\n")
        if not self.has_key("dates"):
            self["dates"] = dates
        return dates


    # Methods to modify pinboard.in content

    def add(self, url, description, extended="", tags=(), date="", toread="no", replace="no"):
        """Add a new post to pinboard.in"""
        query = {}
        query["url"] = url
        query ["description"] = description
        query["toread"] = toread
        query["replace"] = replace
        if extended:
            query["extended"] = extended
        if tags and (isinstance(tags, TupleType) or isinstance(tags, ListType)):
            query["tags"] = " ".join(tags)
        elif tags and (StringTypes and isinstance(tags, StringTypes)) or \
                (not StringTypes and (isinstance(tags, StringType) or \
                isinstance(tags, UnicodeType))):
            query["tags"] = tags

        # This is a rather rudimentary way of parsing date strings into
        # ISO8601 dates: if the date string is shorter than the required
        # 20 characters then it is assumed that it is a partial date
        # such as "2005-3-31" or "2005-3-31T20:00" and it is split into a
        # list along non-numerals. Empty elements are then removed
        # and then this is passed to the tuple/list case where
        # the tuple/list is padded with necessary 0s and then formatted
        # into an ISO8601 date string. This does not take into account
        # time zones.
        if date and (StringTypes and isinstance(tags, StringTypes)) or \
                (not StringTypes and (isinstance(tags, StringType) or \
                isinstance(tags, UnicodeType))) and len(date) < 20:
            date = re.split("\D", date)
            while '' in date:
                date.remove('')
        if date and (isinstance(date, ListType) or isinstance(date, TupleType)):
            date = list(date)
            if len(date) > 2 and len(date) < 6:
                for i in range(6 - len(date)):
                    date.append(0)
            query["dt"] = "%.4d-%.2d-%.2dT%.2d:%.2d:%.2dZ" % tuple(date)
        elif date and (datetime and (isinstance(date, datetime.datetime) \
                or isinstance(date, datetime.date))):
            query["dt"] = "%.4d-%.2d-%.2dT%.2d:%.2d:%.2dZ" % date.utctimetuple()[:6]
        elif date:
            query["dt"] = date
        try:
            response = self.__request("%s/posts/add?%s" % (PINBOARD_API, \
                    urllib.urlencode(query)))
            if response.firstChild.getAttribute("code") != u"done":
                raise AddError
            if _debug:
                sys.stderr.write("Post, %s (%s), added to pinboard.in\n" \
                        % (description, url))
        except:
            if _debug:
                sys.stderr.write("Unable to add post, %s (%s), to pinboard.in\n" \
                        % (description, url))

    def bundle(self, bundle, tags):
        """Bundle a set of tags together"""
        query = {}
        query["bundle"] = bundle
        if tags and (isinstance(tags, TupleType) or isinstance(tags, ListType)):
            query["tags"] = " ".join(tags)
        elif tags and isinstance(tags, StringTypes):
            query["tags"] = tags
        try:
            response = self.__request("%s/tags/bundles/set?%s" % (PINBOARD_API, \
                    urllib.urlencode(query)))
            if response.firstChild.getAttribute("code") != u"done":
                raise BundleError
            if _debug:
                sys.stderr.write("Tags, %s, bundled into %s.\n" \
                        % (repr(tags), bundle))
        except:
            if _debug:
                sys.stderr.write("Unable to bundle tags, %s, into %s to pinboard.in\n" \
                        % (repr(tags), bundle))

    def delete(self, url):
        """Delete post from pinboard.in by its URL"""
        try:
            response = self.__request("%s/posts/delete?%s" % (PINBOARD_API, \
                    urllib.urlencode({"url":url})))
            if response.firstChild.getAttribute("code") != u"done":
                raise DeleteError
            if _debug:
                sys.stderr.write("Post, %s, deleted from pinboard.in\n" \
                        % url)
        except:
            if _debug:
                sys.stderr.write("Unable to delete post, %s, from pinboard.in\n" \
                    % url)

    def delete_bundle(self, name):
        """Delete bundle from pinboard.in by its name"""
        try:
            response = self.__request("%s/tags/bundles/delete?%s" % (PINBOARD_API, \
                    urllib.urlencode({"bundle":name})))
            if response.firstChild.getAttribute("code") != u"done":
                raise DeleteBundleError
            if _debug:
                sys.stderr.write("Bundle, %s, deleted from pinboard.in\n" \
                        % name)
        except:
            if _debug:
                sys.stderr.write("Unable to delete bundle, %s, from pinboard.in\n" \
                    % name)

    def rename_tag(self, old, new):
        """Rename a tag"""
        query = {"old":old, "new":new}
        try:
            response = self.__request("%s/tags/rename?%s" % (PINBOARD_API, \
                    urllib.urlencode(query)))
            if response.firstChild.getAttribute("code") != u"done":
                raise RenameTagError
            if _debug:
                sys.stderr.write("Tag, %s, renamed to %s\n" \
                        % (old, new))
        except:
            if _debug:
                sys.stderr.write("Unable to rename %s tag to %s in pinboard.in\n" \
                    % (old, new))


