# -*- coding: utf-8 -*-


class EncodingUtils():
    def __init__(self):
        pass

    def to_unicode(self, obj, encoding='utf-8'):
        """
        Returns an encoded string into unicode
        """
        if isinstance(obj, basestring):
            if not isinstance(obj, unicode):
                obj = unicode(obj, encoding)

        return obj