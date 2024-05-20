

def foo(**kw):
    print(kw["d"])
    print(type(kw))


d = 1
b = 2
c = 3

foo(d=d, b=b, c=c)