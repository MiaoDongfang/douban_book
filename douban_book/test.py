#list = [('Tom',4),('Jack',7),('Daly',9),('Mary',1),('God',5),('Yuri',3)]
list = [['Tom',4],['Jack',7],['Daly',9],['Mary',1],['God',5],['Yuri',3]]
print list
list.sort(lambda x,y:cmp(x[1],y[1]))
print list

print list[1][1]

for i in range(5):
    print i

list2=[]
for i in range(len(list)):

    list2.append(list[i][0])

print list2