#!/usr/bin/env python3
"""
Teste de compressão com gzip para comparação
"""

import gzip
import os
import shutil
import subprocess
import time


def testar_gzip():
    """Testa compressão gzip no mesmo arquivo usado no experimento 3.1"""

    arquivo_base = "silesia/dickens"

    if not os.path.exists(arquivo_base):
        print(f"Erro: {arquivo_base} não encontrado")
        return

    tamanho_original = os.path.getsize(arquivo_base)
    print(f"\n{'=' * 80}")
    print(f"TESTE GZIP - Arquivo: {arquivo_base}")
    print(f"{'=' * 80}")
    print(
        f"Tamanho original: {tamanho_original:,} bytes ({tamanho_original / (1024**2):.2f} MB)\n"
    )

    # COMPRESSÃO
    print("Comprimindo com gzip (nível padrão -6)...")
    tempo_inicio = time.time()

    with open(arquivo_base, "rb") as f_in:
        with gzip.open("dickens.gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    tempo_comp = time.time() - tempo_inicio
    tamanho_comp = os.path.getsize("dickens.gz")
    taxa = (tamanho_comp / tamanho_original) * 100
    bits_simbolo = (tamanho_comp * 8) / tamanho_original

    print(f"✓ Compressão concluída")
    print(f"  Tempo: {tempo_comp:.2f} s")
    print(f"  Tamanho comprimido: {tamanho_comp:,} bytes")
    print(f"  Taxa: {taxa:.2f}%")
    print(f"  Bits/símbolo: {bits_simbolo:.4f}\n")

    # DESCOMPRESSÃO
    print("Descomprimindo...")
    tempo_inicio = time.time()

    with gzip.open("dickens.gz", "rb") as f_in:
        with open("dickens_descomp", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    tempo_decomp = time.time() - tempo_inicio

    print(f"✓ Descompressão concluída")
    print(f"  Tempo: {tempo_decomp:.2f} s\n")

    # Verificar integridade
    tamanho_descomp = os.path.getsize("dickens_descomp")
    if tamanho_descomp == tamanho_original:
        print("✓ Verificação de integridade: OK\n")
    else:
        print("✗ Erro: tamanhos diferentes!\n")

    # Limpar arquivos temporários
    os.remove("dickens.gz")
    os.remove("dickens_descomp")

    # Resultados
    print(f"{'=' * 80}")
    print("RESULTADOS GZIP")
    print(f"{'=' * 80}")
    print(f"Taxa de compressão: {taxa:.2f}%")
    print(f"Bits/símbolo: {bits_simbolo:.4f}")
    print(f"Tempo compressão: {tempo_comp:.2f} s")
    print(f"Tempo descompressão: {tempo_decomp:.2f} s")
    print(f"Tempo total: {tempo_comp + tempo_decomp:.2f} s")
    print(f"\nComparação com melhor PPMC (k=5):")
    print(f"  PPMC: 1.916 bits/s (23.95%), tempo comp: 60.35s")
    print(
        f"  gzip: {bits_simbolo:.3f} bits/s ({taxa:.2f}%), tempo comp: {tempo_comp:.2f}s"
    )

    return {
        "taxa": taxa,
        "bits_simbolo": bits_simbolo,
        "tempo_comp": tempo_comp,
        "tempo_decomp": tempo_decomp,
        "tamanho_comp": tamanho_comp,
    }


if __name__ == "__main__":
    testar_gzip()
