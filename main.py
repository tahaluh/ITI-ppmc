import argparse

from arithmetic import (
    codificar_intervalo,
    decodificar_simbolo,
    finalizar_encoder,
    inicializar_decoder,
    inicializar_encoder,
)

ESC = 256

modelo = {}
eventos = []


def decodificar_evento(contexto):
    excluidos = set()

    for j in range(len(contexto) + 1):
        subcontexto = contexto[j:]
        frequencias = obter_frequencias(subcontexto, excluidos)
        cumulativos, total = construir_cumulativos(frequencias)

        simbolo_encontrado = decodificar_simbolo(cumulativos, total)

        if simbolo_encontrado == ESC:
            if subcontexto:
                if subcontexto in modelo:
                    excluidos.update(modelo[subcontexto].keys())
                continue
            raise ValueError("Símbolo de escape encontrado no contexto vazio.")
        return simbolo_encontrado, subcontexto, excluidos.copy()

    raise ValueError("Falha ao decodificar símbolo real.")


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

    if contexto:  # não é contexto vazio
        frequencias = {s: tabela[s] for s in simbolos_validos}
        frequencias[ESC] = 1
        return frequencias

    frequencias = {s: 1 for s in range(256) if s not in excluidos}
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


def salvar_arquivo_comprimido(output_path, kmax, tamanho_original, codigo_final):
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(f"{kmax}\n")
        outfile.write(f"{tamanho_original}\n")
        outfile.write("".join(map(str, codigo_final)) + "\n")


def comprimir(input_path, output_path, kmax):
    print(f"Comprimindo {input_path} para {output_path} com kmax={kmax}...")

    with open(input_path, "rb") as infile:
        data = infile.read()

        inicializar_encoder()
        for i in range(len(data)):
            # atual kmax anteiores
            contexto = data[max(0, i - kmax) : i]
            simbolo = data[i]
            # print(f"contexto: {contexto}, simbolo: {simbolo}")

            eventos_simbolo = procurar_simbolo(contexto, simbolo)

            codificar_eventos(eventos_simbolo)

            eventos.extend(eventos_simbolo)

            atualizar_modelo(contexto, simbolo)

        codigo_final = finalizar_encoder()
        print(f"Código final: {codigo_final}")
        salvar_arquivo_comprimido(output_path, kmax, len(data), codigo_final)
        # exibe modelo
        # print("\nModelo de frequências:")
        # print(modelo)
        # print(f"Eventos: {eventos}")


def descomprimir(input_path, output_path, kmax):
    print(f"Descomprimindo {input_path} para {output_path} com kmax={kmax}...")

    with open(input_path, "r", encoding="utf-8") as infile:
        kmax = int(infile.readline().strip())
        tamanho_original = int(infile.readline().strip())

        # array de bytes do código final
        bitstream = infile.readline().strip()
        bits = [int(b) for b in bitstream]

        print(
            f"kmax: {kmax}, tamanho original: {tamanho_original}, código final: {bits}"
        )

        inicializar_decoder(bits)

        saida = bytearray()

        while len(saida) < tamanho_original:
            # contexto descomprimido
            contexto = bytes(saida[max(0, len(saida) - kmax) :])

            simbolo, _, _ = decodificar_evento(contexto)
            if simbolo is None:
                print("Erro: símbolo não encontrado durante a descompressão.")
                break

            saida.append(simbolo)
            atualizar_modelo(contexto, simbolo)

        with open(output_path, "wb") as outfile:
            outfile.write(saida)
        print(f"Descompressão concluída. Saída salva em {output_path}.")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", type=int, choices=[0, 1], help="0=comprimir, 1=descomprimir"
    )
    parser.add_argument("kmax", type=int, help="Valor numerico de kmax")
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = "input.txt"
    output_path = "output.ppmc"
    output_path_descomprimido = "output_descomprimido.txt"

    if args.mode == 0:
        comprimir(input_path, output_path, args.kmax)
    else:
        descomprimir(output_path, output_path_descomprimido, args.kmax)


if __name__ == "__main__":
    main()
