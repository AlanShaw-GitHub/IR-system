def vector_encode(a, l):
    return list(i in a for i in l)
	
	
def vector_decode(v, l):
    ret = []
    for i in range(len(v)):
        if v[i]:
            ret.append(l[i])
    return ret

def boolean_op(op, stack):
    if op == 'AND':
        vec1 = stack.pop()
        vec2 = stack.pop()
        res = list(map(lambda x,y: x and y, vec1, vec2))
    elif op == 'OR':
        vec1 = stack.pop()
        vec2 = stack.pop()
        res = list(map(lambda x,y: x or y, vec1, vec2))
    elif op == 'NOT':
        vec1 = stack.pop()
        res = list(map(lambda x: not x, vec1))
    stack.append(res)		
    return stack