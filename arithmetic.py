PRECISAO = 32

MAX_INTERVALO = (1 << PRECISAO) - 1
METADE = 1 << (PRECISAO - 1)
PRIMEIRO_QUARTO = METADE >> 1
TERCEIRO_QUARTO = PRIMEIRO_QUARTO * 3


encoder = {"baixo": 0, "alto": MAX_INTERVALO, "bits_pendentes": 0, "bits": []}


def inicializar_encoder():
    encoder["baixo"] = 0
    encoder["alto"] = MAX_INTERVALO
    encoder["bits_pendentes"] = 0
    encoder["bits"] = []


def escrever_bit(bit):
    encoder["bits"].append(bit)

    while encoder["bits_pendentes"] > 0:
        encoder["bits"].append(1 - bit)
        encoder["bits_pendentes"] -= 1


def codificar_intervalo(inicio, fim, total):
    baixo = encoder["baixo"]
    alto = encoder["alto"]

    intervalo_atual = alto - baixo + 1

    novo_alto = baixo + (intervalo_atual * fim // total) - 1
    novo_baixo = baixo + (intervalo_atual * inicio // total)

    baixo = novo_baixo
    alto = novo_alto

    while True:
        if alto < METADE:
            escrever_bit(0)

        elif baixo >= METADE:
            escrever_bit(1)
            baixo -= METADE
            alto -= METADE

        elif baixo >= PRIMEIRO_QUARTO and alto < TERCEIRO_QUARTO:
            encoder["bits_pendentes"] += 1
            baixo -= PRIMEIRO_QUARTO
            alto -= PRIMEIRO_QUARTO

        else:
            break

        baixo <<= 1
        alto <<= 1
        alto |= 1

    encoder["baixo"] = baixo
    encoder["alto"] = alto


def finalizar_encoder():
    encoder["bits_pendentes"] += 1

    if encoder["baixo"] < PRIMEIRO_QUARTO:
        escrever_bit(0)
    else:
        escrever_bit(1)

    return encoder["bits"]


decoder = {"baixo": 0, "alto": MAX_INTERVALO, "codigo": 0, "bits": [], "pos": 0}


def ler_bit():
    if decoder["pos"] < len(decoder["bits"]):
        bit = decoder["bits"][decoder["pos"]]
        decoder["pos"] += 1
        return bit
    return 0


def inicializar_decoder(bits):
    decoder["baixo"] = 0
    decoder["alto"] = MAX_INTERVALO
    decoder["codigo"] = 0
    decoder["bits"] = bits
    decoder["pos"] = 0

    for _ in range(PRECISAO):
        decoder["codigo"] = (decoder["codigo"] << 1) | ler_bit()


def decodificar_simbolo(cumulativos, total):
    """Decodifica um simbolo no intervalo atual e atualiza o estado do decoder."""
    baixo = decoder["baixo"]
    alto = decoder["alto"]
    codigo = decoder["codigo"]

    intervalo_atual = alto - baixo + 1
    valor = ((codigo - baixo + 1) * total - 1) // intervalo_atual

    simbolo_encontrado = None
    inicio_encontrado = None
    fim_encontrado = None

    for simbolo, (inicio, fim) in cumulativos.items():
        if inicio <= valor < fim:
            simbolo_encontrado = simbolo
            inicio_encontrado = inicio
            fim_encontrado = fim
            break

    if simbolo_encontrado is None:
        raise ValueError("Simbolo nao encontrado durante a decodificacao.")

    alto = baixo + (intervalo_atual * fim_encontrado // total) - 1
    baixo = baixo + (intervalo_atual * inicio_encontrado // total)

    while True:
        if alto < METADE:
            pass
        elif baixo >= METADE:
            baixo -= METADE
            alto -= METADE
            codigo -= METADE
        elif baixo >= PRIMEIRO_QUARTO and alto < TERCEIRO_QUARTO:
            baixo -= PRIMEIRO_QUARTO
            alto -= PRIMEIRO_QUARTO
            codigo -= PRIMEIRO_QUARTO
        else:
            break

        baixo <<= 1
        alto <<= 1
        alto |= 1
        codigo = (codigo << 1) | ler_bit()

    decoder["baixo"] = baixo
    decoder["alto"] = alto
    decoder["codigo"] = codigo

    return simbolo_encontrado
