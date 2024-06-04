# Emojicode Transpiler

## Visão Geral

Este projeto é um transpilador que converte um código-fonte escrito em uma linguagem de programação baseada em emojis (emojicode) para Python. Ele é uma linguagem tipada com atual suporte a tipos de declarações primários como strings e números, operações e estruturas de controle, usando uma combinação de emojis para representar diferentes elementos sintáticos.

## Estrutura do Projeto

- `token_specification`: Especifica os diferentes tokens reconhecidos pela linguagem de entrada, cada um associado a uma expressão regular para correspondência.
- `tokenize`: Função que converte o código-fonte em uma lista de tokens.
- `Parser`: Classe responsável por analisar a lista de tokens e construir a árvore sintática abstrata (AST).
- `SemanticAnalyzer`: Classe que realiza a análise semântica na AST para garantir que não existam erros de tipo ou variáveis indefinidas.
- `Transpiler`: Classe que converte a AST em código Python.

## Como Usar

### Requisitos

- Python 3.x

### Passos

- **Clone o repositório:**
  ```bash
  git clone https://github.com/Tutuviz/emojicode
  cd emojicode
  ```
- **Crie um arquivo de código emojicode:**
  Crie um arquivo de entrada (`example.pye`) contendo o código em emojicode.
- **Execute o transpiler:**
  ```bash
  python pymoji.py --in example.pye --out example.py
  ```
  Isso transpilará o código emojicode para Python e salvará o resultado em `example.py`.
- **Opcionalmente, execute o código Python transpile:**
  ```bash
  python pymoji.py --in example.pye --out example.py --run
  ```
  Isso transpilará o código e imediatamente executará o arquivo Python resultante.
  ### Argumentos da Linha de Comando
  - `--in <arquivo>`: Especifica o arquivo de entrada contendo o código emojicode. O padrão é `example.pye`.
  - `--out <arquivo>`: Especifica o arquivo de saída para o código Python transpile. O padrão é `example.py`.
  - `--run`: Executa o código Python transpile após a conversão.
  - `--debug`: Exibe informações de depuração durante a execução. [Em Progresso...]
  ### Exibir a Ajuda
  Para ver a ajuda sobre o uso do script, execute:
  ```bash
  python pymoji.py --help
  ```
  Você verá a seguinte saída:
  ```bash
  usage: pymoji.py [-h] [--in INPUT FILE] [--out OUTPUT FILE] [--run] [--debug]
  
  Transpile Python code and optionally run it.
  options:

    -h, --help            show this help message and exit
    --in INPUT FILE       input Python file path (default: example.pye)
    --out OUTPUT FILE     output transpiled file path (default: example.py)
    --run                 run the transpiled code
    --debug               print debug information
  ```
  ## Estrutura do Código Emojicode
  Aqui está uma visão geral dos tokens e seus significados:
  - `▶️`: Início do programa.
  - `⏹️`: Fim do programa.
  - `🧵`: Declaração de variável string.
  - `🔢`: Declaração de variável numérica.
  - `✳️`: Declaração de variável booleana.
  - `📥`: Entrada.
  - `📤`: Saída.
  - `🌪️`: Aspas para String.
  - `✅` e `❎`: Valores booleanos.
  - `🍷🗿`: Início de uma condicional `if`.
  - `☝️🤓`: `else` em uma condicional.
  - `🔓` e `🔒`: Delimitação de blocos de código.
  - `😍😍`: Operador lógico `AND`.
  - `😘🤨`: Operador lógico `OR`.
  - `♊`, `♓`, `🐜`, `🐘`, `🐜🐞`, `🐘🦣`: Operadores de comparação.
  - `🤰`, `🔫`, `🙅`, `🇦🇴`: Operadores aritméticos.
  - `🐳`: Loop `while`.
  - `🔂`: Loop `for`.
  - `⛳`: Delimitação de range em um loop `for`.

## Exemplo de Código Emojicode

### Exemplo 01

```
▶️

🧵 senha_padrao = 🌪️senha123🌪️

🧵 usuario = 📥🌪️Digite o nome de usuário: 🌪️
🧵 senha = 📥🌪️Digite a senha: 🌪️

🐳 usuario ♓ 🌪️admin🌪️ 😘🤨 senha ♓ senha_padrao 🔓
  📤 🌪️Usuário ou senha incorretos. Tente novamente.🌪️
  usuario = 📥🌪️Digite o nome de usuário: 🌪️
  senha = 📥🌪️Digite a senha: 🌪️
🔒

📤 🌪️Login bem-sucedido! Bem-vindo!🌪️

⏹️
```

Este código implementa um simples sistema de autenticação que solicita ao usuário que insira um nome de usuário e uma senha. Ele continuará pedindo essas informações até que o usuário insira `admin` como nome de usuário e `senha123` como senha. Uma vez que as credenciais corretas sejam inseridas, o programa exibe uma mensagem de login bem-sucedido.

### Exemplo 02

```
▶️

🧵 num1 = 📥🌪️Digite um numero: 🌪️
🧵 num2 = 📥🌪️Digite um numero: 🌪️

🍷🗿 num1 ♓ num2 🔓
  📤 🌪️Os numeros sao diferentes🌪️
🔒 ☝️🤓 🔓
  📤 🌪️Os numeros sao iguais🌪️
🔒

⏹️
```

Este código simples solicita ao usuário que insira dois números e verifica se os números são iguais ou diferentes. Se os números forem diferentes, uma mensagem indicando isso é exibida. Se os números forem iguais, uma mensagem indicando isso é exibida.

### Exemplo 03

```
▶️

🔢 num1 = 0
🔢 num2 = 1

🔢 total = 0

🔂 i ⛳ 15 🔓
  📤 num1
  total = num1 🤰 num2
  num1 = num2
  num2 = total
🔒

⏹️
```

Este código em Emojicode gera os primeiros 15 números da sequência de Fibonacci e os exibe. Ele utiliza duas variáveis, `num1` e `num2`, para calcular os números subsequentes na sequência, seguindo a regra de que cada número é a soma dos dois números anteriores.

## Futuras melhorias

 - [ ] Concatenação de Strings
 - [ ] Melhoria da mensagem de erro com adição da linha
 