import argparse

from arithmetic import codificar_intervalo

ESC = 256

modelo = {}
eventos = []


def codificar_eventos(eventos_simbolo):
    for contexto, simbolo, excluidos in eventos_simbolo:
        codificar_evento(contexto, simbolo, excluidos)


def codificar_evento(contexto, evento, excluidos):
    frequencias = obter_frequencias(contexto, excluidos, evento)
    cumulativos, total = construir_cumulativos(frequencias)

    inicio, fim = cumulativos[evento]

    codificar_intervalo(inicio, fim, total)


def construir_cumulativos(frequencias):
    cumulativos = {}
    acumulado = 0

    # ordenacao deterministica
    for simbolo in sorted(frequencias.keys()):
        freq = frequencias[simbolo]
        cumulativos[simbolo] = (acumulado, acumulado + freq)
        acumulado += freq

    total = acumulado

    return cumulativos, total


def obter_frequencias(contexto, excluidos, evento=None):
    if contexto in modelo:
        simbolos_contexto = set(modelo[contexto].keys())
        tabela = modelo[contexto]
    else:
        simbolos_contexto = set()
        tabela = {}

    simbolos_validos = simbolos_contexto - excluidos

    frequencias = {s: tabela[s] for s in simbolos_validos}

    if contexto:  # não é contexto vazio
        frequencias[ESC] = 1
    elif evento is not None:  # contexto vazio, simbolo novo
        frequencias[evento] = 1

    return frequencias


def procurar_simbolo(contexto, simbolo):
    eventos = []
    excluidos = set()

    for j in range(len(contexto) + 1):
        subcontexto = contexto[j:]

        if subcontexto in modelo:
            simbolos_contexto = set(modelo[subcontexto].keys())
        else:
            simbolos_contexto = set()

        simbolos_validos = simbolos_contexto - excluidos

        if simbolo in simbolos_validos:
            eventos.append((subcontexto, simbolo, excluidos.copy()))
            return eventos

        if subcontexto:
            # desce contexto
            eventos.append((subcontexto, ESC, excluidos.copy()))
            excluidos.update(simbolos_contexto)
        else:
            # novo simbolo
            eventos.append((subcontexto, simbolo, excluidos.copy()))

    return eventos


def atualizar_modelo(contexto, simbolo):
    for j in range(len(contexto) + 1):
        # verifica modelo
        subcontexto = contexto[j:]
        # print(f"  subcontexto: {subcontexto}")

        if subcontexto not in modelo:
            # simbolo novo, adc no modelo
            modelo[subcontexto] = {}

        if simbolo not in modelo[subcontexto]:
            modelo[subcontexto][simbolo] = 0

        modelo[subcontexto][simbolo] += 1


def comprimir(input_path, output_path, kmax):
    print(f"Comprimindo {input_path} para {output_path} com kmax={kmax}...")

    with open(input_path, "rb") as infile:
        data = infile.read()

        for i in range(len(data)):
            # atual kmax anteiores
            contexto = data[max(0, i - kmax) : i]
            simbolo = data[i]
            # print(f"contexto: {contexto}, simbolo: {simbolo}")

            eventos_simbolo = procurar_simbolo(contexto, simbolo)

            codificar_eventos(eventos_simbolo)

            eventos.extend(eventos_simbolo)

            atualizar_modelo(contexto, simbolo)

        # exibe modelo
        # print("\nModelo de frequências:")
        # print(modelo)
        print(f"Eventos: {eventos}")


def descomprimir(kmax):
    print(f"Descomprimindo com kmax={kmax}...")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("kmax", type=int, help="Valor numerico de kmax")
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = "input.txt"
    output_path = "output.ppmc"

    comprimir(input_path, output_path, args.kmax)


if __name__ == "__main__":
    main()
