import pickle
def isint(x):
    try:
        int(x)
        return True
    except ValueError:
        return False
with open('waitlist.txt', 'rb') as fp:
    li=pickle.load(fp)
print(li)
while True:
    inp=input()
    if inp=="":
        break
    elif inp=="-":
        li.remove(li[int(input())])
    elif isint(inp):
        t=li[:int(inp)]
        t.append(input())
        li=t+li[int(inp):]
    else:
        li.append(inp)
    print(li)
with open('waitlist.txt', 'wb') as fp:
    pickle.dump(li,fp)
print("quit",li)
