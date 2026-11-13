
from cache_simulator_GUI import CacheLine, MRU

def testar_mru():
    linha1 = CacheLine()
    linha2 = CacheLine()
    linha3 = CacheLine()

    linha1.last_access_time = 5
    linha2.last_access_time = 15
    linha3.last_access_time = 10

    vitima = MRU().find_victim([linha1, linha2, linha3])

    assert vitima is linha2, "ERRO: MRU escolheu a linha errada!"
    print("TESTE APROVADO: MRU substitui a linha mais recentemente utilizada.")

if __name__ == "__main__":
    testar_mru()
