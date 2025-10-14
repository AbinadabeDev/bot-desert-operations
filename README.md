<div align="center">

# 🤖 Automação para Desert Operations - Python Selenium

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/selenium-4.0-green.svg)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Multiplataforma-lightgrey.svg)]()

**Assistente automatizado para troca de recursos premium no jogo Desert Operations com interface CLI e Selenium**

[Sobre](#-sobre-o-projeto) • [Funcionalidades](#-principais-funcionalidades) • [Tecnologias](#️-tecnologias) • [Instalação](#-instalação) • [Como Usar](#-como-usar) • [Arquitetura](#️-arquitetura) • [Contato](#-contato)

</div>

---

## 📋 Sobre o Projeto

Este projeto é um **bot de automação para o jogo online Desert Operations**, desenvolvido em Python utilizando Selenium. Ele automatiza o processo de troca de recursos premium, navegando em múltiplos iframes, lendo taxas de câmbio em tempo real e fornecendo interação via linha de comando para controlar as operações.

O bot contempla navegação robusta para menus complexos, captura dinâmica de dados da página e simulação de interações humanas para ajustar sliders e confirmar trocas.

### 🎯 Problema Resolvido

Realizar trocas de recursos manualmente no jogo pode ser repetitivo e sujeito a erros, especialmente pela interface com iframes aninhados e timers dinâmicos.

**Solução**: Automação total com monitoramento dos timers, ajuste preciso das quantidades via teclado simulado e confirmação das operações, poupando tempo e garantindo eficiência nas trocas.

---

## ✨ Principais Funcionalidades

- 🔐 **Login manual inicial**, seguido por automação da sessão
- 🕹️ **Navegação em iframes aninhados** para acessar menus complexos
- 📊 **Extração de dados dinâmicos** como taxas de câmbio e tempo restante para atualização
- ⌨️ **Interface de linha de comando (CLI)** para interação direta e configuração de parâmetros
- 🎛️ **Controle de sliders via simulação de teclas** para ajustar a quantidade de recursos
- ✅ **Execução autônoma do ciclo de espera, atualização e troca**
- 🚪 **Gestão de pop-ups (lightboxes) e foco em múltiplas abas do navegador**
- ⚙️ **Tratamento de exceções e logs detalhados para monitoramento**

---

## 🛠️ Tecnologias

### Stack Principal

| Tecnologia   | Versão  | Aplicação                         |
|--------------|---------|----------------------------------|
| **Python**   | 3.8+    | Linguagem de programação          |
| **Selenium** | 4.x     | Automação de navegador web        |
| **ChromeDriver** | Compatível | Driver para automação no Chrome |
| **Logging**  | Built-in| Monitoramento e debug             |

### Conceitos Técnicos Aplicados

- **Manipulação de iframes e múltiplas abas** com Selenium para automação web avançada
- **Espera dinâmica inteligente** para capturar elementos com timers variáveis
- **Parsing robusto de strings e formatação de tempo**
- **Simulação de interações do usuário (teclado e cliques)**
- **Gerenciamento de estado da interface (pop-ups, confirmações)**
- **Uso de logging para feedback detalhado no console**
- **Validação e sanitização de entradas numéricas**

---

## 📦 Instalação

### Pré-requisitos

- **Python 3.8 ou superior** ([Download](https://www.python.org/downloads/))
- **Google Chrome** instalado (ou outro navegador compatível)
- **ChromeDriver** compatível com sua versão do Chrome ([Download](https://sites.google.com/a/chromium.org/chromedriver/))
- **Biblioteca Selenium** (instalação com pip)

### Passo a Passo

**1. Clone ou baixe o código-fonte**
git clone https://github.com/seu-usuario/desert-operations-bot.git
cd desert-operations-bot

**2. Instale a dependência do Selenium**
pip install selenium

**3. Configure o ChromeDriver**

- Coloque o executável do ChromeDriver em uma pasta do PATH ou no mesmo diretório do script

**4. Execute o bot**

python bot_desert_operations.py

---

## 🚀 Como Usar

### Inicialização

- Faça login manualmente na página do jogo após o script abrir o navegador
- Pressione ENTER na linha de comando para iniciar a automação

### Configuração

- Defina a quantidade padrão de diamantes para cada troca, respeitando o saldo disponível

### Funcionamento

- O bot aguardará automaticamente o timer de atualização das taxas
- Atualiza a página para capturar novas taxas em tempo real
- Realiza trocas sequenciais com quantidade definida para cada recurso
- Gerencia pop-ups e confirmações para garantir sucesso nas operações

### Interrupção

- Use Ctrl+C no terminal para interromper o bot com segurança

---

## 🏗️ Arquitetura

### Estrutura do Código

Bot estruturado em funções com responsabilidades claras:

- **Configurações iniciais:** URLs, locators e variáveis globais
- **Funções utilitárias:** parsing, formatação e validação de inputs
- **Funções Selenium:** navegação, interação e controle do navegador
- **Funções de negócio:** obtenção de dados, cálculo e lógica de troca
- **Loop principal:** controle de ciclos de espera, atualização e execução das trocas

### Destaques Técnicos

- Uso de WebDriverWait com condições customizadas para sincronização
- Parsing customizado de tempo e valores formatados no padrão brasileiro
- Manipulação avançada de iframes e janelas no navegador
- Uso de logging para facilitar monitoramento e depuração

---

## 🔮 Melhorias Futuras

- [ ] Interface gráfica para facilitar uso sem linha de comando
- [ ] Integração com múltiplas contas e sessões simultâneas
- [ ] Implementação de notificações e alertas em caso de erros
- [ ] Otimização do controle dos sliders para maior rapidez
- [ ] Suporte a outros navegadores além do Chrome
- [ ] Persistência de configurações em arquivo JSON/YAML

---

## 💡 Por Que Este Projeto?

Este bot é uma demonstração de domínio avançado em automação web com Python e Selenium, além da capacidade de lidar com interfaces complexas e dados dinâmicos. Ideal para jogadores e entusiastas que buscam otimizar tarefas repetitivas em jogos online, poupando tempo e evitando erros manuais.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Contato

**Abinadabe Oliveira**

- 💼 LinkedIn: [Abinadabe Oliveira](https://www.linkedin.com/in/abinadabedev/)
- 🐙 GitHub: [@AbinadabeDev](https://github.com/AbinadabeDev)
- 📧 Email: [abinadabedev@gmail.com](mailto:abinadabedev@gmail.com)
- 🌐 Portfólio: [abinadabedev.github.io](https://abinadabedev.github.io)
---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela no repositório!**

Desenvolvido com 💜 e ☕ por Abinadabe Oliveira

</div>


