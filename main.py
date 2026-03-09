import argparse

ESC = 256

modelo = {}
eventos = []


def procurar_simbolo(contexto, simbolo):
    eventos = []
    for j in range(len(contexto) + 1):
        # verifica modelo
        subcontexto = contexto[j:]

        if subcontexto in modelo and simbolo in modelo[subcontexto]:
            eventos.append(subcontexto)
        # fora do alfabeto
        eventos.append(ESC)

    return None


def atualizar_modelo(contexto, simbolo):
    for j in range(len(contexto) + 1):
        # verifica modelo
        subcontexto = contexto[j:]
        print(f"  subcontexto: {subcontexto}")

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
            print(f"contexto: {contexto}, simbolo: {simbolo}")

            contexto_encontrado = procurar_simbolo(contexto, simbolo)

            if contexto_encontrado is None:
                eventos.append
            else:
                eventos.append()

            atualizar_modelo(contexto, simbolo)

        # exibe modelo
        print("\nModelo de frequências:")
        print(modelo)


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
