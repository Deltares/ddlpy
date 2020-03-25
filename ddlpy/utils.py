import dateutil.rrule
import itertools

def date_series(start, end, freq=dateutil.rrule.MONTHLY):
    """return a list of start and end date over the timespan start[->end following the frequency rule"""
    def pairwise(it):
        """return all sequential pairs"""
        # loop over the iterator twice.
        # tee it so we don't consume it twice
        it0, it1 = itertools.tee(it)
        i0 = itertools.islice(it0, None)
        i1 = itertools.islice(it1, 1, None)
        # merge to a list of pairs
        return zip(i0, i1)

    # go over the rrule, also include the end, return consequitive pairs
    result = list(
        pairwise(
            list(
                dateutil.rrule.rrule(dtstart=start, until=end, freq=freq)
            ) + [end]
        )
    )
    # remove last one if empty (first of month until first of month)
    if len(result) > 1 and result[-1][0] == result[-1][1]:
        # remove it
        del result[-1]
    return result
