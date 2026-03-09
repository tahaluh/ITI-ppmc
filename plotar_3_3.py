import matplotlib.pyplot as plt
import os

# Ler arquivo progressivo se existir
if os.path.exists('output_progressivo.txt'):
    posicoes, comprimentos = [], []
    arquivo_nomes = {}
    offset = 0
    
    # Mapeamento de arquivos (precisa ser extraído do cabeçalho do .ppmc)
    # Por enquanto, usar aproximação visual
    
    with open('output_progressivo.txt') as file:
        next(file)
        for linha in file:
            parts = linha.strip().split(',')
            if len(parts) == 3:
                posicoes.append(int(parts[0]))
                comprimentos.append(float(parts[2]))
    
    plt.figure(figsize=(14, 7))
    plt.plot(posicoes, comprimentos, linewidth=1, marker='o', markersize=2)
    plt.xlabel('Posição no arquivo combinado (bytes)')
    plt.ylabel('Comprimento médio (bits/símbolo)')
    plt.title('Comprimento Médio Progressivo - Corpus Silesia')
    plt.grid(True, alpha=0.3)
    plt.savefig('grafico_3_3_silesia.png', dpi=100)
    print('Gráfico salvo em: grafico_3_3_silesia.png')
    plt.show()
else:
    print('Arquivo output_progressivo.txt não encontrado')
