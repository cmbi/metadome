
def convertListOfIntegerToRanges(self, p):
    """Converts a list of integer to a list of ranges.
    Source: http://stackoverflow.com/questions/4628333/converting-a-list-of-integers-into-range-in-python"""
    if len(p) > 0:
        q = sorted(p)
        i = 0
        for j in range(1,len(q)):
            if q[j] > 1+q[j-1]:
                yield (q[i],q[j-1])
                i = j
        yield (q[i], q[-1])