import pbapi

def all_by_tag(**kwargs):
    """
        This is a sample function to demonstrate how I envision using the library.
        Required arguments:
            username = Your Pinboard username
            password = Your Pinboard password
            tag      = 'foo bar baz'  1-3 times separated by spaces

        Output Parameters:
            json_string representation of the data objects pulled from the pinboard API.
            Aside from mild cleanup its all the data pulled.  The tags upon return are an array, instead of a space
            seperated string.  The idea is to use this to build complex data structures you can easily manipulate later.
    """ 
    import simplejson
    # TODO This is to check for the required arguments. has to be a better way 
    for item in ['username','password','tag']:
        if item not in kwargs: raise pbapi.pbexcept.AddError('','Provide [username,password,tag]')

    def _tag_result(tags):
        """ simple private function to iterate the response """
        output = []
        for post in tags:
            temp_store = {}
            for k,v in post.iteritems():
                if k == 'tags':
                    temp_store[k] = []
                    temp_store[k].extend(v.split())
                else:
                    temp_store[k] = v
            output.append(temp_store)
        return output
        
    username  = kwargs['username']
    pass_word = kwargs['password'] 
    tag       = kwargs['tag']
    api = pbapi.connect.PinboardAPI()
    api.install(username,pass_word)    
    account = pbapi.account.PinboardAccount()
    tagged_posts = account.all(tag=tag)
    try:
        json_str = simplejson.dumps(
                       _tag_result(tagged_posts)
                       )
    except:
        raise pbapi.pbexcept.GetError('','json failure')
    else:
        return json_str
