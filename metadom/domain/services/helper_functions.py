
def convertListOfIntegerToRanges(p):
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
    
def list_of_stringified_of_ranges(p):
    """Creates a list of strings representing the ranges built in convertListOfIntegerToRanges
    used for pretty printing"""
    return [str(y[0])+"-"+str(y[1]) if y[0]!=y[1] else str(y[0]) for y in p]
        
def create_sliding_window(total_length, sliding_window_size):
    region_sliding_window = []
    for i in range(total_length):
        if sliding_window_size <= 0:
            region_i_start=i
            region_i_stop=i
            
            windowrange = range(region_i_start, region_i_stop)
            region_sliding_window.append({'sw_range':windowrange, 'sw_coverage':1.0})
        
        else:
            region_i_start = i-(sliding_window_size)
            region_i_stop = i+(sliding_window_size)+1
        
            if region_i_start < 0:
                region_i_start = 0
            if region_i_stop >= total_length:
                region_i_stop = total_length;
            
            windowrange = range(region_i_start, region_i_stop)
            region_sliding_window.append({'sw_range':windowrange, 'sw_coverage':len(windowrange)/((sliding_window_size*2)+1)})
    
        
    return region_sliding_window
