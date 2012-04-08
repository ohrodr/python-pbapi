import datetime
from pbapi.connect.request import Request

class PinboardAccount(dict):
    """A pinboard.in account class
       This class contains the main methods for operating on a
       pinboard account via the public https API
    """

    # override methods
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
            self._postschanged = 1
        return dict.__setitem__(self, key, value)


    ## API parse methods
    def suggest_parse(self,data):
        from xml.dom.minidom import parseString
        multi_line = ''
        for line in data: multi_line += line
        dom  = parseString(multi_line)
        popular = dom.getElementsByTagName("popular")
        recommended = dom.getElementsByTagName("recommended")
        popular_tags = []
        recommended_tags = []
        for tag in popular: popular_tags.append(tag.firstChild.wholeText)
        for tag in recommended: recommended_tags.append(tag.firstChild.wholeText)
        return {'popular':popular_tags,
                'recommended':recommended_tags }

    ## api methods
    def suggest(self,suggest_url):
        """
           Given an input URL retrieve suggested tags
           popular tags as defined by the API are global
           recommended tags as defined by the API are user based
           input as a string
           output { 'popular':[],'recommended':[]}
        """
        from pbapi import API_URL
        request = Request()
        parm = (('url',suggest_url),
                ('format','xml'))
        suggest_subpath = '/posts/suggest'
        suggest_api_url = '%s%s' %( API_URL ,suggest_subpath)
        request.seturl(suggest_api_url)
        suggest_parm = (('url',suggest_url),('format','xml'))
        for parm in suggest_parm: request.add_parm(parm)
        request._request() 
        results = self.suggest_parse(request.data)
        return results

    def get_parse(self,data):
        import simplejson
        import re
        multi_line = ''
        for line in data: multi_line += line.rstrip()
        sanitized_json = re.sub('}{','},{',multi_line)
        print multi_line
        json_string = simplejson.loads(sanitized_json)
        return json_string

    def get(self,**kwargs):
        from pbapi import API_URL
        request = Request()
        get_subpath = '/posts/get'
        get_api_url = '%s%s' %( API_URL,get_subpath )
        request.seturl(get_api_url)

        get_parm = {'format':'json'}
        if ('date' in kwargs) and ('url' in kwargs): raise pbapi.pbexcept.GetError
        if 'tag'  in kwargs: get_parm['tag'] = kwargs['tag']
        if 'date' in kwargs: get_parm['dt']  = kwargs['date']
        if 'url'  in kwargs: get_parm['url'] = kwargs['url']
        for k,v in get_parm.iteritems(): request.add_parm((k,v))
        request._request()
        results = self.get_parse(request.data) 
        return results
