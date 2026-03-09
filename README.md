# Compressor PPMC (Prediction by Partial Matching)

Implementação do algoritmo PPMC com codificação aritmética para compressão de arquivos.

## Requisitos

- Python 3.x

## Uso

### Comprimir arquivo

```bash
python3 main.py 0 <kmax> [opções]
```

**Parâmetros:**
- `0`: modo compressão
- `<kmax>`: tamanho máximo do contexto (recomendado: 2-4)

**Opções:**
- `--janela [N]`: ativa monitoramento por janela (padrão: 1000 se não especificar N)
- `--pct-reset <percentual>`: percentual de piora para reset do modelo (padrão: 10.0)

**Exemplos:**

```bash
# Compressão simples com kmax=4
python3 main.py 0 4

# Compressão com monitoramento de janela (tamanho 1000)
python3 main.py 0 4 --janela

# Compressão com janela customizada e threshold de reset
python3 main.py 0 4 --janela 2000 --pct-reset 15
```

**Entrada/Saída:**
- Arquivo de entrada: configurado no código (padrão: `dickens`)
- Arquivo de saída: `output.ppmc`

### Descomprimir arquivo

```bash
python3 main.py 1 <kmax> [opções]
```

**Parâmetros:**
- `1`: modo descompressão
- `<kmax>`: deve ser o mesmo usado na compressão

**Exemplos:**

```bash
# Descompressão simples
python3 main.py 1 4

# Descompressão (janela é ignorada na descompressão, mas pode ser passada)
python3 main.py 1 4 --janela
```

**Entrada/Saída:**
- Arquivo de entrada: `output.ppmc`
- Arquivo de saída: `descomprimido/<nome_original>` (pasta criada automaticamente)

## Formato do arquivo comprimido (.ppmc)

```
<kmax>
<tamanho_original>
<nome_original>
<num_bits>
<dados_binários>
```

## Monitoramento de taxa local e reset

Quando `--janela` é ativado, o compressor:
1. Monitora a média de bits/símbolo em janelas adjacentes de tamanho especificado
2. Se a média da janela atual exceder a anterior por mais de `pct-reset`%, o modelo é resetado
3. Um marcador de reset é inserido no fluxo para sincronizar o descompressor

## Observações

- Para arquivos grandes (>10MB), a compressão pode demorar devido à complexidade do algoritmo PPMC
- Recomenda-se usar `kmax` menor (2-3) para arquivos grandes
- O arquivo comprimido usa formato binário real (não texto) para máxima eficiência
- Logs de progresso aparecem a cada 1000 símbolos processados
