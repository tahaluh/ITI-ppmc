import argparse
import os

from arithmetic import (
    codificar_intervalo,
    decodificar_simbolo,
    encoder,
    finalizar_encoder,
    inicializar_decoder,
    inicializar_encoder,
)

ESC = 256
RESET = 257

modelo = {}


def reset_modelo():
    modelo.clear()


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
    comprimento_total = 0.0

    for contexto, simbolo, excluidos in eventos_simbolo:
        comprimento_total += codificar_evento(contexto, simbolo, excluidos)

    return comprimento_total


def codificar_evento(contexto, evento, excluidos):
    bits_antes = len(encoder["bits"])

    frequencias = obter_frequencias(contexto, excluidos, evento)
    cumulativos, total = construir_cumulativos(frequencias)

    inicio, fim = cumulativos[evento]

    codificar_intervalo(inicio, fim, total)

    # Comprimento real observado: quantidade de bits efetivamente emitidos.
    bits_depois = len(encoder["bits"])
    return bits_depois - bits_antes


def construir_cumulativos(frequencias):
    cumulativos = {}
    acumulado = 0

    # A ordem de insercao e deterministica entre compressor e descompressor.
    for simbolo, freq in frequencias.items():
        cumulativos[simbolo] = (acumulado, acumulado + freq)
        acumulado += freq

    total = acumulado

    return cumulativos, total


def obter_frequencias(contexto, excluidos, evento=None):
    tabela = modelo.get(contexto, {})

    if contexto:  # nao e contexto vazio
        frequencias = {s: f for s, f in tabela.items() if s not in excluidos}
        frequencias[ESC] = 1
        return frequencias

    frequencias = {s: 1 for s in range(256) if s not in excluidos}
    if RESET not in excluidos:
        frequencias[RESET] = 1
    return frequencias


def procurar_simbolo(contexto, simbolo):
    eventos_local = []
    excluidos = set()
    tamanho_contexto = len(contexto)

    for j in range(tamanho_contexto + 1):
        subcontexto = contexto[j:]
        tabela = modelo.get(subcontexto)

        if tabela and simbolo in tabela and simbolo not in excluidos:
            eventos_local.append((subcontexto, simbolo, excluidos))
            return eventos_local

        if subcontexto:
            eventos_local.append((subcontexto, ESC, excluidos))
            if tabela:
                excluidos = excluidos | set(tabela.keys())
        else:
            eventos_local.append((subcontexto, simbolo, excluidos))

    return eventos_local


def atualizar_modelo(contexto, simbolo):
    tamanho_contexto = len(contexto)
    for j in range(tamanho_contexto + 1):
        subcontexto = contexto[j:]

        if subcontexto not in modelo:
            modelo[subcontexto] = {}

        tabela = modelo[subcontexto]
        if simbolo in tabela:
            tabela[simbolo] += 1
        else:
            tabela[simbolo] = 1


def bits_para_bytes(bits):
    """Converte lista de bits em bytes."""
    # Padding para multiplo de 8
    num_bits = len(bits)
    padding = (8 - num_bits % 8) % 8
    bits_padded = bits + [0] * padding

    bytes_data = bytearray()
    for i in range(0, len(bits_padded), 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | bits_padded[i + j]
        bytes_data.append(byte)

    return bytes_data, num_bits


def bytes_para_bits(bytes_data, num_bits):
    """Converte bytes de volta para lista de bits."""
    bits = []
    for byte in bytes_data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    return bits[:num_bits]


def salvar_arquivo_comprimido(
    output_path, kmax, tamanho_original, nome_original, codigo_final
):
    bytes_data, num_bits = bits_para_bytes(codigo_final)

    with open(output_path, "wb") as outfile:
        # Cabecalho em texto
        header = f"{kmax}\n{tamanho_original}\n{nome_original}\n{num_bits}\n"
        outfile.write(header.encode("utf-8"))
        # Bits em binario
        outfile.write(bytes_data)


def comprimir(input_path, output_path, kmax, janela=None, pct_reset=10.0):
    print(f"Comprimindo {input_path} para {output_path} com kmax={kmax}...")

    if janela is not None:
        print(f"Monitoramento local ativo: janela={janela}, pct_reset={pct_reset}%")

    with open(input_path, "rb") as infile:
        data = infile.read()

        reset_modelo()
        inicializar_encoder()

        media_janela_anterior = None
        soma_bits_janela = 0.0
        itens_janela = 0
        total_bytes = len(data)

        for i in range(len(data)):
            # Log de progresso a cada 1000 símbolos
            if i > 0 and i % 100000 == 0:
                progresso = (i / total_bytes) * 100
                print(f"Progresso: {i}/{total_bytes} bytes ({progresso:.1f}%)")

            # atual kmax anteiores
            contexto = data[max(0, i - kmax) : i]
            simbolo = data[i]
            # print(f"contexto: {contexto}, simbolo: {simbolo}")

            eventos_simbolo = procurar_simbolo(contexto, simbolo)

            comprimento_simbolo = codificar_eventos(eventos_simbolo)

            atualizar_modelo(contexto, simbolo)

            if janela is not None:
                soma_bits_janela += comprimento_simbolo
                itens_janela += 1

                if itens_janela == janela:
                    media_janela_atual = soma_bits_janela / itens_janela

                    if (
                        media_janela_anterior is not None
                        and media_janela_atual
                        > media_janela_anterior * (1 + pct_reset / 100.0)
                    ):
                        # Emite marcador de reset para manter sincronia no decoder.
                        contexto_reset = data[max(0, i - kmax + 1) : i + 1]
                        eventos_reset = procurar_simbolo(contexto_reset, RESET)
                        codificar_eventos(eventos_reset)
                        reset_modelo()

                    media_janela_anterior = media_janela_atual
                    soma_bits_janela = 0.0
                    itens_janela = 0

        codigo_final = finalizar_encoder()
        print(f"Compressao finalizada: {len(codigo_final)} bits gerados")
        nome_original = os.path.basename(input_path)
        salvar_arquivo_comprimido(
            output_path, kmax, len(data), nome_original, codigo_final
        )
        # exibe modelo
        # print("\nModelo de frequências:")
        # print(modelo)
        # print(f"Eventos: {eventos}")


def descomprimir(input_path, kmax, janela=None, pct_reset=10.0):
    print(f"Descomprimindo {input_path} com kmax={kmax}...")

    with open(input_path, "rb") as infile:
        # Le cabecalho em texto
        lines = []
        current_line = bytearray()
        while len(lines) < 4:
            byte = infile.read(1)
            if not byte:
                break
            if byte == b"\n":
                lines.append(current_line.decode("utf-8"))
                current_line = bytearray()
            else:
                current_line.extend(byte)

        kmax = int(lines[0])
        tamanho_original = int(lines[1])
        nome_original = lines[2]
        num_bits = int(lines[3])

        # Le bits em binario
        bytes_data = infile.read()
        bitstream = bytes_para_bits(bytes_data, num_bits)

        print(f"kmax: {kmax}, tamanho original: {tamanho_original}, bits: {num_bits}")

        reset_modelo()
        inicializar_decoder(bitstream)

        saida = bytearray()

        while len(saida) < tamanho_original:
            # Log de progresso a cada 1000 símbolos
            if len(saida) > 0 and len(saida) % 100000 == 0:
                progresso = (len(saida) / tamanho_original) * 100
                print(
                    f"Progresso: {len(saida)}/{tamanho_original} bytes ({progresso:.1f}%)"
                )

            # contexto descomprimido
            contexto = bytes(saida[max(0, len(saida) - kmax) :])

            simbolo, _, _ = decodificar_evento(contexto)
            if simbolo is None:
                print("Erro: símbolo não encontrado durante a descompressão.")
                break

            if simbolo == RESET:
                reset_modelo()
                continue

            saida.append(simbolo)
            atualizar_modelo(contexto, simbolo)

        output_dir = "descomprimido"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, nome_original)

        with open(output_path, "wb") as outfile:
            outfile.write(saida)
        print(f"Descompressão concluída. Saída salva em {output_path}.")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "mode", type=int, choices=[0, 1], help="0=comprimir, 1=descomprimir"
    )
    parser.add_argument("kmax", type=int, help="Valor numerico de kmax")
    parser.add_argument(
        "--janela",
        type=int,
        nargs="?",
        const=1000,
        default=None,
        help="Tamanho da janela para monitoramento. Sem valor usa 1000; sem flag desativa.",
    )
    parser.add_argument(
        "--pct-reset",
        type=float,
        default=10.0,
        help="Percentual de piora entre janelas para acionar reset (padrao: 10.0).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = "dickens"
    output_path = "output.ppmc"

    if args.mode == 0:
        comprimir(input_path, output_path, args.kmax, args.janela, args.pct_reset)
    else:
        descomprimir(output_path, args.kmax, args.janela, args.pct_reset)


if __name__ == "__main__":
    main()
