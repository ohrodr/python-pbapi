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

    """
       The following methods are paired to the relevant API methods """
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
        """ this is the private get_parse method """
        import simplejson
        import re
        multi_line = ''
        for line in data: multi_line += line.rstrip()
        sanitized_json = re.sub('}{','},{',multi_line)
        json_string = simplejson.loads(sanitized_json)
        return json_string

    def get(self,**kwargs):
        """ get method for the API """
        from pbapi import API_URL
        request = Request()
        get_subpath = '/posts/get'
        get_api_url = '%s%s' %( API_URL,get_subpath )
        request.seturl(get_api_url)

        get_parm = {'format':'json'}
        if ('date' in kwargs) and ('url' in kwargs): raise GetError
        if 'tag'  in kwargs: get_parm['tag'] = kwargs['tag']
        if 'date' in kwargs: get_parm['dt']  = kwargs['date']
        if 'url'  in kwargs: get_parm['url'] = kwargs['url']
        if 'meta'  in kwargs: get_parm['meta'] = kwargs['meta']
        for k,v in get_parm.iteritems(): request.add_parm((k,v))
        request._request()
        results = self.get_parse(request.data) 
        return results

    def update_parse(self,data):
        """ this is the private update_parse method """
        from xml.dom.minidom import parseString
        import time
        multi_line = ''
        for line in data: multi_line += line
        dom  = parseString(multi_line)
        update = dom.getElementsByTagName("update")[0].getAttribute('time')
        # 2012-04-07T20:50:00Z
        time_fmt = '%Y-%m-%dT%H:%M:%SZ'
        update_time = time.strptime(update,time_fmt)
        return update_time

    def update(self):
        """ update method for the API """
        from pbapi import API_URL
        request = Request()
        update_subpath = '/posts/update'
        update_api_url = '%s%s' %( API_URL,update_subpath )
        request.seturl(update_api_url)
        get_parm = {'format':'json'}
        
        for k,v in get_parm.iteritems(): request.add_parm((k,v))
        request._request()
        return self.update_parse(request.data)

    def add_parse(self,data):
        """ this is the private add_parse method """
        from xml.dom.minidom import parseString
        import time
        multi_line = ''
        for line in data: multi_line += line
        dom = parseString(multi_line)
        result = dom.getElementsByTagName("result")[0].getAttribute('code')
        return result 

    def add(self,**kwargs):
        """ add method for the API """
        from pbapi import API_URL
        from pbapi import pbexcept
        add_subpath = '/posts/add'
        add_api_url = '%s%s' %( API_URL,add_subpath )
        add_parm = { }

        request = Request()
        request.seturl(add_api_url)

        # simple verification check
        if ('description' not in kwargs) and ('url' not in kwargs): 
            raise pbexcept.AddError('','Missing required Parameters [description,url] to add')
        add_parm['description'] = add_parm['extended'] = kwargs['description']
        add_parm['url'] = kwargs['url']

        possible_parms = ['tags','date','replace','shared','toread','extended']
        for k in possible_parms: 
            if k in kwargs: 
                add_parm[k] = kwargs[k] 
        for k,v in add_parm.iteritems(): request.add_parm((k,v))
        request._request()
        return self.add_parse(request.data) 

    def delete_parse(self,data):
        from xml.dom.minidom import parseString
        multi_line = ''
        for line in data: multi_line += line
        dom = parseString(multi_line)
        result = dom.getElementsByTagName("result")[0]
        return result.getAttribute('code')

    def delete(self,url):
        """ delete method for the API """
        from pbapi import API_URL
        from pbapi import pbexcept
        del_subpath = '/posts/delete'
        del_api_url = '%s%s' %( API_URL, del_subpath )
        del_parm = {'url':url}

        request = Request()
        request.seturl(del_api_url)
        request.add_parm(('url',url))
        request._request()
        return self.delete_parse(request.data)

    def recent_parse(self,data):
        from xml.dom.minidom import parseString
        multi_line = ''
        for line in data: multi_line += line
        dom = parseString(multi_line)
        posts = dom.getElementsByTagName("posts")
        result_data = {}

        for post in posts: 
            owner = post.getAttribute('user')
            if owner not in result_data:
                result_data[owner] = {'posts':[]}
            post_set = post.getElementsByTagName("post")
            for p in post_set:
                url = p.getAttribute('href')
                description = p.getAttribute('description')
                extended = p.getAttribute('extended')
                post_hash = p.getAttribute('hash')
                tag  = p.getAttribute('tag')
                post_time = p.getAttribute('time')
                result_data[owner]['posts'].append({
                    'url'        : url,
                    'description': description,
                    'extended'   : extended,
                    'hash'       : post_hash,
                    'tag'        : tag.split(),
                    'time'       : post_time,
                    }) 
        return result_data
                  
    def recent(self,**kwargs):
        from pbapi import API_URL
        from pbapi import pbexcept
        recent_subpath = '/posts/recent'
        recent_api_url = '%s%s' %( API_URL, recent_subpath )
        recent_parm = {}
        if ('tag' in kwargs):
            recent_parm['tag']   = kwargs['tag'] 
        elif ('count' in kwargs):
            recent_parm['count'] = kwargs['count'] 
    
        request = Request()
        request.seturl(recent_api_url)
        for k,v in recent_parm.iteritems(): request.add_parm((k,v))
        request._request()
        return self.recent_parse(request.data)

    def dates_parse(self,data):
        from xml.dom.minidom import parseString
        multi_line = ''
        for line in data: multi_line += line
        dom = parseString(multi_line)
        dates = dom.getElementsByTagName('dates')
        output_data = {}

        for date in dates:
            user = date.getAttribute('user')
            tag = date.getAttribute('tag')
            date = date.getElementsByTagName('date')
            if user not in output_data: 
                output_data[user] = {}
            if tag not in output_data[user]:
                output_data[user][tag] = []
            for d in date:
                output_data[user][tag].append({'count' : d.getAttribute('count'),
                                               'date'  : d.getAttribute('date'),})
        return output_data

    def dates(self,**kwargs):
        from pbapi import API_URL,pbexcept
        dates_subpath = '/posts/dates'
        dates_api_url = '%s%s' %( API_URL, dates_subpath )
        dates_parm = {}
        if 'tag' in kwargs: dates_parm['tag'] = kwargs['tag'].split()

        request = Request()
        request.seturl(dates_api_url)
        for k,v in dates_parm.iteritems(): request.add_parm(('tag',kwargs['tag']))
        request._request()
        return self.dates_parse(request.data)

    def all_parse(self,data):
        import simplejson
        multi_line = ''
        for line in data: multi_line += line
        json_output = simplejson.loads(multi_line)
        return json_output
            
    def all(self,**kwargs):
        from pbapi import API_URL, pbexcept
        possible_keys = ['tag','start','results','fromdt','todt','meta']
        all_subpath = '/posts/all'
        all_api_url = '%s%s' %( API_URL, all_subpath )
        all_parm = {'format':'json'}
        for k in possible_keys:
            if k not in kwargs:
                continue
            else:
                all_parm[k] = kwargs[k]
        request = Request()
        request.seturl(all_api_url)
        for k,v in all_parm.iteritems(): request.add_parm((k,v))
        request._request()
        return self.all_parse(request.data)

    def tags_set_parse(self,data):
        from xml.dom.minidom import parseString
        multi_line = ''
        for line in data: multi_line += line
        dom = parseString(multi_line)
        tags = dom.getElementsByTagName('tags')[0]
        output = {}
        for tag in tags.getElementsByTagName('tag'):
            output[tag.getAttribute('tag')] = tag.getAttribute('count')
        return output

    def tags_get(self):
        from pbapi import API_URL, pbexcept
        tags_get_subpath = '/tags/get'
        tags_api_url = '%s%s' %( API_URL, tags_get_subpath )
        
        request = Request()
        request.seturl(tags_api_url)
        request._request()
        return self.tags_set_parse(request.data)

    def tags_delete(self,tag):
        from pbapi import API_URL, pbexcept
        tags_delete_subpath = '/tags/delete'
        tags_delete_api_url = '%s%s' %( API_URL, tags_delete_subpath )
        tags_parm = {}
        request = Request()
        request.seturl(tags_delete_api_url)
        request.add_parm(('tag',tag))
         
        request._request()
        return self.add_parse(request.data)

    def tags_rename(self,old_tag,new_tag):
        from pbapi import API_URL, pbexcept
        tags_rename_subpath = '/tags/rename'
        tags_rename_api_url = '%s%s' %( API_URL, tags_rename_subpath )
        tags_rename_parm = {'old':old_tag,'new':new_tag }
        
        request = Request()
        request.seturl(tags_rename_api_url)
        for k,v in tags_rename_parm.iteritems(): request.add_parm((k,v))
        request._request()
        return self.add_parse(request.data)
