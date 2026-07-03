[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/qwtGOM5t)
# template-notebooks

Template para atividades de implementação baseados em notebooks Jupyter com ambiente
reprodutível usando [Pixi](https://pixi.prefix.dev/latest/).

Este repositório serve como ponto de partida para estudos computacionais,
experimentos numéricos, análises de dados e atividades didáticas em que é
importante que outras pessoas consigam instalar o mesmo ambiente e reproduzir os
notebooks com o mínimo possível de configuração manual.

## Objetivos

- Padronizar projetos de notebooks usados em atividades científicas e
  acadêmicas.
- Facilitar a reprodução dos resultados por alunos e colaboradores.
- Evitar problemas comuns de ambiente, como versões diferentes de Python,
  NumPy, SciPy, Jupyter ou outras bibliotecas.
- Manter notebooks e scripts auxiliares organizados e formatados.

## Conteúdo do repositório

- `pixi.toml`: define o ambiente computacional do projeto e as tarefas
  disponíveis.
- `pixi.lock`: registra as versões resolvidas das dependências para melhorar a
  reprodutibilidade.
- `.pre-commit-config.yaml`: configura verificações automáticas de formatação e
  limpeza dos notebooks.
- `jupytext.toml`: configura o uso do Jupytext para sincronizar notebooks
  `.ipynb` com arquivos texto equivalentes, quando aplicável.
- `scripts/sync_notebooks.py`: sincroniza notebooks usando Jupytext.
- `notebooks/`: diretório esperado para os notebooks do projeto.

Se o diretório `notebooks/` ainda não existir no seu clone local, crie-o antes
de adicionar novos notebooks:

```sh
mkdir -p notebooks
```

## Como usar

### 1. Instale o Pixi

Este projeto usa o Pixi para criar um ambiente isolado e reprodutível. Isso
significa que as bibliotecas usadas nos notebooks ficam separadas das
bibliotecas instaladas no restante do seu computador.

Instale o Pixi seguindo a documentação oficial:

<https://pixi.prefix.dev/latest/installation/>

Depois da instalação, feche e abra novamente o terminal. Para conferir se o
Pixi está disponível, rode:

```sh
pixi --version
```

### 2. Baixe o repositório

Clone o repositório:

```sh
git clone https://github.com/lncc-ga020/template-notebooks.git
```

Entre na pasta do projeto:

```sh
cd template-notebooks
```

### 3. Instale o ambiente do projeto

Dentro da pasta do projeto, rode:

```sh
pixi install --frozen
```

O argumento `--frozen` instrui o Pixi a respeitar o arquivo `pixi.lock`. Isso é
importante para que todos usem, tanto quanto possível, as mesmas versões das
dependências.

### 4. Ative o ambiente

Depois da instalação, ative o ambiente:

```sh
pixi shell
```

Quando o ambiente está ativo, comandos como `python`, `jupyter`, `ruff` e
`pre-commit` passam a usar as versões definidas pelo projeto.

### 5. Abra os notebooks

Com o ambiente Pixi ativo, você pode abrir o JupyterLab:

```sh
jupyter lab
```

Depois disso, abra os arquivos `.ipynb` dentro do diretório `notebooks/`.

Também é possível usar o VS Code. Nesse caso, uma forma prática é abrir o VS
Code a partir do terminal em que o ambiente Pixi já está ativo:

```sh
code .
```

No VS Code, abra o notebook desejado e selecione o interpretador Python do
ambiente Pixi do projeto. Se você usa VS Code com frequência, também é
recomendável instalar uma extensão para integração com ambientes Pixi.

## Fluxo de trabalho recomendado

1. Atualize sua cópia local do repositório antes de começar a trabalhar:

   ```sh
   git pull
   ```

2. Ative o ambiente:

   ```sh
   pixi shell
   ```

3. Abra o JupyterLab ou o VS Code.

4. Trabalhe nos notebooks dentro de `notebooks/`.

5. Antes de enviar alterações, rode:

   ```sh
   pixi run precommit-sync
   ```

Esse comando sincroniza os notebooks com Jupytext e executa as verificações de
formatação configuradas para o projeto.

## Configuração para desenvolvimento

Se você pretende modificar notebooks, scripts ou arquivos do projeto, instale os
hooks do `pre-commit` depois de clonar o repositório:

```sh
pixi shell
pre-commit install
```

Isso instala verificações automáticas que rodam antes de cada commit. Elas ajudam
a manter os notebooks limpos, padronizados e mais fáceis de revisar.

Se você clonar este repositório novamente em outra pasta do computador, será
necessário rodar `pre-commit install` também nessa nova cópia.

## Tarefas Pixi úteis

Alguns comandos já estão definidos em `pixi.toml`:

```sh
pixi run notebooks-smoke
```

Lista os notebooks encontrados em `notebooks/`. É uma verificação rápida para
confirmar que o diretório de notebooks está organizado.

```sh
pixi run notebooks-sync
```

Sincroniza notebooks `.ipynb` com Jupytext.

```sh
pixi run precommit
```

Executa as verificações do `pre-commit` em todos os arquivos.

```sh
pixi run precommit-sync
```

Sincroniza os notebooks e depois executa as verificações do `pre-commit`.

## Boas práticas para notebooks científicos

- Coloque notebooks principais em `notebooks/`.
- Use nomes descritivos, por exemplo `analise_dados_experimento_01.ipynb`.
- Evite depender de arquivos que existem apenas no seu computador.
- Registre no próprio notebook quais dados, parâmetros e hipóteses foram usados.
- Mantenha células em uma ordem que permita executar o notebook do começo ao
  fim.
- Sempre que possível, defina sementes aleatórias em simulações estocásticas.

## Arquivos gerados localmente

O `.gitignore` deste projeto ignora alguns diretórios e arquivos comuns de saída,
como:

- `tmp/`
- `outputs/`
- `refs/`
- arquivos `.csv`
- figuras `.png` dentro de `notebooks/`

Isso ajuda a evitar que resultados temporários ou arquivos grandes sejam
versionados por engano. Se algum arquivo de resultado for essencial para o
projeto, discuta antes de adicioná-lo ao Git.

## Problemas comuns

### O comando `pixi` não foi encontrado

Provavelmente o Pixi não foi instalado ou o terminal ainda não reconheceu a nova
instalação. Feche e abra o terminal. Se o problema continuar, revise as
instruções oficiais de instalação do Pixi.

### O notebook não encontra uma biblioteca Python

Confirme que você ativou o ambiente correto:

```sh
pixi shell
```

Se estiver usando VS Code, confira também se o kernel selecionado pertence ao
ambiente Pixi deste projeto.

### As verificações falharam antes do commit

Rode:

```sh
pixi run precommit-sync
```

Algumas correções podem ser feitas automaticamente. Depois disso, revise os
arquivos modificados, execute novamente o comando se necessário e faça o commit.

## Licença

Este projeto usa a licença MIT. Veja o arquivo `LICENSE`.

## Declaração de uso de IA

A revisão, refatoração e implementação deste template foi/é assistida por IA. LLMs utilizadas:

- OpenAI Codex;
- Github Copilot.

## Apoio institucional

Este projeto recebe apoio institucional do
[Laboratório Nacional de Computação Científica (LNCC)](https://www.gov.br/lncc/pt-br),
unidade de pesquisa do Ministério da Ciência, Tecnologia e Inovação (MCTI),
Brasil.

<p align="center">
  <a href="https://www.gov.br/lncc/pt-br">
    <img src="resources/logo/lncc-mcti.svg" alt="LNCC (MCTI) logo" width="820">
  </a>
</p>
