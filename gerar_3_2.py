#!/usr/bin/env python3
"""
Gerar experimento 3.2 - Aprendizado progressivo
"""

import os
import subprocess
import time


def gerar_experimento_3_2():
    """Gera dados e gráfico para experimento 3.2"""

    print("\n" + "=" * 80)
    print("EXPERIMENTO 3.2 - Aprendizado Progressivo")
    print("=" * 80)

    # Usar dickens para ser mais rápido
    arquivo = "silesia/dickens"

    if not os.path.exists(arquivo):
        print(f"Erro: {arquivo} não encontrado")
        return

    print(f"\nComprimindo {arquivo} com kmax=4 e modo progressivo...")

    tempo_inicio = time.time()
    cmd = ["python3", "main.py", "0", "4", arquivo, "--progressivo"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        tempo = time.time() - tempo_inicio

        if result.returncode != 0:
            print(f"Erro na compressão: {result.stderr}")
            return

        print(f"✓ Compressão concluída em {tempo:.1f}s")

        if not os.path.exists("output_progressivo.txt"):
            print("✗ Arquivo output_progressivo.txt não gerado")
            return

        print("✓ Dados progressivos gerados\n")

        # Gerar gráfico
        gerar_grafico()

    except Exception as e:
        print(f"Erro: {e}")


def gerar_grafico():
    """Gera o gráfico de aprendizado progressivo"""
    try:
        import matplotlib.pyplot as plt

        print("Gerando gráfico...")

        dados = []
        with open("output_progressivo.txt") as f:
            for linha in f:
                if linha.strip():
                    try:
                        pos, bits = map(float, linha.strip().split())
                        comprimento_medio = bits / pos
                        dados.append((pos, comprimento_medio))
                    except:
                        pass

        if not dados:
            print("✗ Nenhum dado válido encontrado")
            return

        x, y = zip(*dados)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(x, y, linewidth=2, color="#2E86AB", label="Comprimento Médio")
        ax.set_xlabel("Posição no arquivo (símbolos)", fontsize=12)
        ax.set_ylabel("Bits/símbolo", fontsize=12)
        ax.set_title("Aprendizado Progressivo - Dickens (kmax=4)", fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.savefig("grafico_3_2_silesia_progressive.png", dpi=150)

        print("✓ Gráfico salvo: grafico_3_2_silesia_progressive.png")

        # Análise
        if len(y) > 0:
            inicio = y[0]
            fim = y[-1]
            reducao = ((inicio - fim) / inicio * 100) if inicio > 0 else 0

            print(f"\n📊 Análise:")
            print(f"   Comprimento inicial:  {inicio:.4f} bits/símbolo")
            print(f"   Comprimento final:    {fim:.4f} bits/símbolo")
            print(f"   Melhoria total:       {reducao:.1f}%")
            print(f"   Pontos coletados:     {len(dados)}")

    except ImportError:
        print("✗ matplotlib não disponível")
    except Exception as e:
        print(f"✗ Erro ao gerar gráfico: {e}")


if __name__ == "__main__":
    gerar_experimento_3_2()
