# -*- coding: utf-8 -*-
from datetime import date

from flask.json import JSONEncoder

from projects.database import Base


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, date):
                return obj.isoformat()
            if isinstance(obj, Base):
                return obj.as_dict()
            iterable = iter(obj)
        except TypeError as e:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)
