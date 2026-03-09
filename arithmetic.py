encoder = {
    "inicio": 0.0,
    "fim": 1.0,
}


def inicializar_encoder():
    encoder["inicio"] = 0.0
    encoder["fim"] = 1.0


def codificar_intervalo(inicio, fim, total):
    intervalo_atual = encoder["fim"] - encoder["inicio"]

    # expande o intervalo
    novo_fim = encoder["inicio"] + intervalo_atual * (fim / total)
    novo_inicio = encoder["inicio"] + intervalo_atual * (inicio / total)

    encoder["inicio"] = novo_inicio
    encoder["fim"] = novo_fim


def finalizar_encoder():
    codigo = (encoder["inicio"] + encoder["fim"]) / 2
    return codigo
