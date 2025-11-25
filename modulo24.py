import asyncio
import random
import time

async def busca_pokemon_kanto():
    ##usando random para gerar um numero float aleatorio de 1 a 5
    tempo_aleatorio=random.uniform(1, 5)
    await asyncio.sleep(tempo_aleatorio)
    #lista que armazena os nomes dos pokemons 

    pokemon_kanto = [
    "Chikorita",
    "Cyndaquil",
    "Totodile",
    "Mareep",
    "Togepi",
    "Houndour",
    "Swinub",
    "Gligar",
    "Teddiursa",
    "Larvitar"
    ]

    #random.randint para gerar um numero inteiro aleatorio de 0 a 9
    numero=random.randint(0, 9)

    return f"Pokemon encontrado em kanto foi {pokemon_kanto[numero]}"

async def busca_pokemon_johto(): 

    ##usando random para gerar um numero float aleatorio de 1 a 5
    tempo_aleatorio=random.uniform(1, 5)
    await asyncio.sleep(tempo_aleatorio)

    #lista que armazena os nomes dos pokemons 
    pokemon_johto = [
        "Bulbasaur",
        "Charmander",
        "Squirtle",
        "Pikachu",
        "Jigglypuff",
        "Meowth",
        "Machop",
        "Geodude",
        "Cubone",
        "Eevee"
    ]

    #random.randint para gerar um numero inteiro aleatorio de 0 a 9
    numero=random.randint(0, 9)

    return f"Pokemon encontrado em johto foi {pokemon_johto[numero]}"
async def busca_pokemon_hoenn():

    ##usando random para gerar um numero float aleatorio de 1 a 5
    tempo_aleatorio=random.uniform(1, 5)
    await asyncio.sleep(tempo_aleatorio)

    #lista que armazena os nomes dos pokemons 
    pokemon_hoenn = [
        "Treecko",
        "Torchic",
        "Mudkip",
        "Ralts",
        "Aron",
        "Carvanha",
        "Numel",
        "Shuppet",
        "Spheal",
        "Beldum"
    ]

    #random.randint para gerar um numero inteiro aleatorio de 0 a 9
    numero=random.randint(0, 9)

    return f"Pokemon encontrado em hoenn foi {pokemon_hoenn[numero]}"

async def busca():

    #armazena o tempo de inicio
    tempo_inicio=time.perf_counter()

    #resultado gurda em formatodo de lista o retorno das funçãoes busca_pokemon_kanto(),busca_pokemon_johto(),busca_pokemon_hoenn()
    resultado=(await asyncio.gather(busca_pokemon_kanto(),busca_pokemon_johto(),busca_pokemon_hoenn()))

    #armazena o tempo de fim
    tempo_fim=time.perf_counter()

    #gera uma str contendo os valores da lista contida na variavel resultado
    resultado_str="\n".join([f"{i}"for i in resultado])

    print(resultado_str)
    print(f"Tempo total de busca:{tempo_fim-tempo_inicio:.2f}")
    
asyncio.run(busca())


