x=[1,23,43,4,5,5,1,2,3]
diz={}
for i in x:
    if i not in diz:
        diz[i]=1
    else:
        diz[i]+=1
for n,v in diz.items():
    if v>1:
        print(n) 
















'''
import asyncio

async def pikachu():
    print("2 pikachu entrou")
    await asyncio.sleep(2)
    print("2 pikachu usou choque do trovao")

async def charmander():
    print("3 charmander entrou")
    await asyncio.sleep(1)
    print("3 charmander usou folhar")

async def batalha():
    await asyncio.gather(pikachu(),charmander())

asyncio.run(batalha())
'''