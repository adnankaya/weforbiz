''' Django notifications signal file '''
# -*- coding: utf-8 -*-
from django.dispatch import Signal

notify = Signal()

"""

notify.send(actor, recipient, verb, action_object, target, level, description, public, timestamp, **kwargs)

"""