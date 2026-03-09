#!/usr/bin/env python3
"""
Gera gráfico do experimento 3.2 a partir dos dados progressivos
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def gerar_grafico_3_2():
    """Gera o gráfico de aprendizado progressivo"""
    print("\n" + "=" * 80)
    print("GERAÇÃO DO GRÁFICO 3.2 - Aprendizado Progressivo")
    print("=" * 80)

    dados = []
    with open("output_progressivo.txt") as f:
        next(f)  # Skip header
        for linha in f:
            if linha.strip():
                try:
                    pos, bits = linha.strip().split()
                    pos = float(pos)
                    bits = float(bits)
                    comprimento_medio = bits / pos if pos > 0 else 0
                    dados.append((pos, comprimento_medio))
                except:
                    pass

    if not dados:
        print("✗ Nenhum dado válido encontrado")
        return

    print(f"✓ {len(dados)} pontos carregados")

    x, y = zip(*dados)
    x_max = x[-1]
    x_milhoes = [v / 1_000_000 for v in x]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(x_milhoes, y, linewidth=2, color="#2E86AB", label="Comprimento medio")
    # Forca o eixo X a ir exatamente do inicio ao ultimo ponto coletado.
    ax.set_xlim(0, x_max / 1_000_000)
    ax.set_xlabel("Posicao no arquivo (milhoes de simbolos)", fontsize=12)
    ax.set_ylabel("Bits/símbolo", fontsize=12)
    ax.set_title("Aprendizado Progressivo - Dickens (kmax=4)", fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Eixo secundario para mostrar percentual do fluxo (0% a 100%)
    ax_top = ax.twiny()
    ax_top.set_xlim(0, x_max / 1_000_000)
    ax_top.set_xlabel("Percentual do fluxo processado", fontsize=11)
    ax_top.xaxis.set_major_formatter(
        FuncFormatter(lambda val, pos: f"{(val * 1_000_000 / x_max) * 100:.0f}%")
    )

    plt.tight_layout()
    plt.savefig("grafico_3_2_silesia_progressive.png", dpi=150)

    print("✓ Gráfico salvo: grafico_3_2_silesia_progressive.png")

    # Análise
    inicio = y[0]
    fim = y[-1]
    reducao = ((inicio - fim) / inicio * 100) if inicio > 0 else 0

    print("\nAnalise:")
    print(f"   Comprimento inicial:  {inicio:.4f} bits/simbolo")
    print(f"   Comprimento final:    {fim:.4f} bits/simbolo")
    print(f"   Melhoria total:       {reducao:.1f}%")
    print(f"   Pontos coletados:     {len(dados)}")

    # Encontrar ponto de estabilização (variação < 1%)
    for i in range(len(y) - 100, 0, -1):
        variacao = abs(y[i] - y[-1]) / y[-1] * 100
        if variacao > 1.0:
            ponto_estab = x[i]
            percent_fluxo = (ponto_estab / x[-1]) * 100
            print(f"\n   Estabilizacao (var < 1%): ~{percent_fluxo:.1f}% do fluxo")
            print(f"   Posicao: ~{int(ponto_estab):,} simbolos")
            break


if __name__ == "__main__":
    gerar_grafico_3_2()
