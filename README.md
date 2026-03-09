# Compressor PPMC (Prediction by Partial Matching)

Implementação do algoritmo PPMC com codificação aritmética para compressão de arquivos.

## Requisitos

- Python 3.x

## Uso

### Comprimir arquivo único

```bash
python3 main.py 0 <kmax> <arquivo>
```

### Comprimir múltiplos arquivos

```bash
python3 main.py 0 <kmax> <arquivo1> <arquivo2> ... <arquivoN> [opções]
```

**Exemplo com Corpus Silesia:**

```bash
python3 main.py 0 4 silesia/dickens silesia/mozilla silesia/xml --janela 1000 --pct-reset 15
```

Neste modo, o compressor:
1. Carrega todos os arquivos sequencialmente
2. Detecta transições entre arquivos e força reset do modelo
3. Monitora taxa local dentro de janelas adaptativas
4. Salva metadados da estrutura no arquivo `.ppmc`

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

## Análise e Testes

### Script de análise completa (3.1, 3.2, 3.3)

Para executar análise completa de performance, aprendizado e transições:

```bash
python3 analise_completa.py
```

Este script executa:

**3.1 - Análise de Ordem e Performance:**
- Testa kmax de 0 a 10
- Registra: bits/símbolo, quantidade de compressão, tempo
- Salva resultados em: `analise_3_1_resultados.csv`

**3.2 - Aprendizado Progressivo (Dickens):**
- Coleta comprimento médio progressivo durante compressão
- Identifica ponto de estabilização no arquivo
- Gera dados para gráfico em `output_progressivo.txt`
- Cria script `plotar_3_2.py` para visualização

**3.3 - Transições e Reset (Corpus Silesia):**
- Comprime múltiplos arquivos do Silesia
- Detecta transições entre arquivos
- Monitora resets automáticos por piora de taxa
- Analisa impacto das transições na compressão

**Aviso:** A análise completa pode levar **1-3 horas** dependendo dos arquivos disponíveis.

Para testar apenas 3.2 (rápido):
```bash
python3 main.py 0 4 dickens --progressivo
python3 plotar_3_2.py
```

### Corpus Silesia

Os arquivos do Corpus Silesia devem estar em: `silesia/`

Arquivos suportados:
- dickens (texto literário)
- mozilla (código)
- mr (dados mistos)
- nci (dados biomédicos)
- ooffice (documento Office)
- osdb (database)
- reymont (MIDI)
- samba (código-fonte)
- sao (SAO database)
- webster (dicionário)
- x-ray (imagem médica)
- xml (dados estruturados)

### Todo o requisito 3.1 e 3.2 pode ser processado com:

```bash
# Teste único com análise de aprendizado
python3 main.py 0 4 silesia/dickens --janela 1000 --pct-reset 15
```
