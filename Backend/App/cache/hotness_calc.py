from datetime import datetime
from math import log

EPOCH = datetime(1970, 1, 1)

def epoch_seconds(date):
    td = date - EPOCH
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)

def calculate_hotness(net_votes: int, created_at: datetime):
    """
    Function that calculates the hotness of a post\n
    net_votes has to be a sum of all (downvotes & upvotes)
    """
    order = log(max(abs(net_votes), 1), 10)
    sign = 1 if net_votes > 0 else -1 if net_votes < 0 else 0
    seconds = epoch_seconds(created_at) - 1134028003
    return round(sign * order + seconds / 45000, 3)