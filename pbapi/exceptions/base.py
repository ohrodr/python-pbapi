
class PinboardError(Exception):
    """Error in the Python-Pinboard module"""
    pass

class ThrottleError(PinboardError):
    """Error caused by pinboard.in throttling requests"""
    def __init__(self, url, message):
        self.url = url
        self.message = message
    def __str__(self):
        return "%s: %s" % (self.url, self.message)

class AddError(PinboardError):
    """Error adding a post to pinboard.in"""
    def __init__(self,url,message):
        self.url = url
        self.message = message
        self.code = -1
    def __str__(self):
        return "ERROR:%i:%s:%s" %(self.code,self.url,self.message)

class GetError(PinboardError):
    """Error adding a post to pinboard.in"""
    pass

class DeleteError(PinboardError):
    """Error deleting a post from pinboard.in"""
    pass

class BundleError(PinboardError):
    """Error bundling tags on pinboard.in"""
    pass

class DeleteBundleError(PinboardError):
    """Error deleting a bundle from pinboard.in"""
    pass

class RenameTagError(PinboardError):
    """Error renaming a tag in pinboard.in"""
    pass

class DateParamsError(PinboardError):
    '''Date params error'''
    pass
