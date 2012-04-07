import datetime

class PinboardAccount(dict):
    """A pinboard.in account"""

    # Used to track whether all posts have been downloaded yet.
    _allposts = 0
    _postschanged = 0

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
            self._postschanged = 1
        return dict.__setitem__(self, key, value)
