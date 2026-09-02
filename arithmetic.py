PRECISAO = 32

MAX_INTERVALO = (1 << PRECISAO) - 1
METADE = 1 << (PRECISAO - 1)
PRIMEIRO_QUARTO = METADE >> 1
TERCEIRO_QUARTO = PRIMEIRO_QUARTO * 3


# Modo legado: bits armazenados como lista de ints 0/1 em encoder["bits"].
# Modo streaming: bits agrupados em bytes e escritos em encoder["_outfile"].
encoder = {
    "baixo": 0,
    "alto": MAX_INTERVALO,
    "bits_pendentes": 0,
    # legado
    "bits": [],
    # streaming
    "bits_count": 0,
    "_outfile": None,
    "_byte_buf": 0,
    "_byte_bits": 0,
}


def inicializar_encoder(outfile=None):
    """outfile: arquivo aberto em 'r+b' para escrita streaming de bytes.
    None = modo legado (acumula bits em lista)."""
    encoder["baixo"] = 0
    encoder["alto"] = MAX_INTERVALO
    encoder["bits_pendentes"] = 0
    encoder["bits"] = []
    encoder["bits_count"] = 0
    encoder["_outfile"] = outfile
    encoder["_byte_buf"] = 0
    encoder["_byte_bits"] = 0


def _emitir_bit(bit):
    """Emite um bit no canal de saida (legado ou streaming)."""
    if encoder["_outfile"] is not None:
        encoder["bits_count"] += 1
        encoder["_byte_buf"] = (encoder["_byte_buf"] << 1) | bit
        encoder["_byte_bits"] += 1
        if encoder["_byte_bits"] == 8:
            encoder["_outfile"].write(bytes([encoder["_byte_buf"]]))
            encoder["_byte_buf"] = 0
            encoder["_byte_bits"] = 0
    else:
        encoder["bits"].append(bit)


def escrever_bit(bit):
    _emitir_bit(bit)
    while encoder["bits_pendentes"] > 0:
        _emitir_bit(1 - bit)
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

    if encoder["_outfile"] is not None:
        # Flush byte parcial com padding de zeros a direita
        if encoder["_byte_bits"] > 0:
            padded = encoder["_byte_buf"] << (8 - encoder["_byte_bits"])
            encoder["_outfile"].write(bytes([padded]))
            encoder["_byte_buf"] = 0
            encoder["_byte_bits"] = 0
        encoder["_outfile"].flush()
        return encoder["bits_count"]

    # Modo legado: retorna lista de bits
    return encoder["bits"]


# ---------------------------------------------------------------------------
# Decoder (inalterado)
# ---------------------------------------------------------------------------

decoder = {"baixo": 0, "alto": MAX_INTERVALO, "codigo": 0, "bits": [], "pos": 0}


def ler_bit():
    if decoder["pos"] < len(decoder["bits"]):
        bit = decoder["bits"][decoder["pos"]]
        decoder["pos"] += 1
        if isinstance(bit, str):
            return 1 if bit == "1" else 0
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
