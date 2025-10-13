<div align="center">

# 🎮 Bot Desert Operations - Assistente de Automação Premium

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-green.svg)](https://selenium.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

*Automação inteligente de trocas de recursos premium no jogo Desert Operations utilizando Python e Selenium WebDriver*

[Características](#-características) •
[Demonstração](#-demonstração) •
[Tecnologias](#️-tecnologias) •
[Instalação](#-instalação) •
[Como Usar](#-como-usar) •
[Arquitetura](#-arquitetura) •
[Contato](#-contato)

</div>

---

## 📋 Sobre o Projeto

Este projeto implementa um **bot autônomo e inteligente** para o jogo de estratégia online [Desert Operations](https://desertoperations.fawkesgames.com/), demonstrando competências avançadas em automação web, manipulação de DOM complexo e criação de soluções robustas com Python[web:8][web:17].

O assistente navega automaticamente pela interface do jogo, extrai dados dinâmicos em tempo real (taxas de câmbio e temporizadores), e executa ciclos completos de trocas de recursos premium de forma autônoma, otimizando a experiência do jogador[web:11][web:14].

### 🎯 Problema Resolvido

No Desert Operations, os jogadores precisam trocar diamantes (moeda premium) por recursos estratégicos em momentos específicos quando as taxas de câmbio são atualizadas. Este processo manual é:
- ⏰ **Demorado**: Requer monitoramento constante das taxas
- 🔁 **Repetitivo**: Múltiplas trocas seguidas de navegação complexa
- ⚠️ **Propenso a erros**: Iframes aninhados e interface dinâmica

**Solução**: Bot totalmente autônomo que monitora, aguarda e executa trocas automaticamente em ciclos configuráveis, liberando o jogador para focar em estratégias.

---

## ✨ Características

### Funcionalidades Principais

- **🤖 Operação Totalmente Autônoma**: Sistema de ciclos automáticos com fases de espera, atualização e execução de trocas
- **⏱️ Sincronização Inteligente**: Captura e interpreta temporizadores dinâmicos para aguardar atualizações de taxas
- **🔄 Fila de Trocas Automatizadas**: Executa sequências completas de 5 recursos com confirmações automáticas
- **🎛️ Ajuste Preciso de Sliders**: Simulação de interações humanas via ActionChains e eventos de teclado
- **🧩 Navegação em Iframes Aninhados**: Manipulação robusta de contextos múltiplos do Selenium WebDriver
- **📊 Extração de Dados Dinâmicos**: Parsing de taxas de câmbio e valores formatados em tempo real
- **🛡️ Tratamento de Erros Robusto**: Sistema de logging detalhado e recuperação de falhas
- **⚙️ Interface Configurável**: Definição de quantidade padrão de diamantes por troca via CLI

### Diferenciais Técnicos

- **Esperas Personalizadas**: Implementação de `WebDriverWait` com condições customizadas (`esperar_pelo_texto_do_timer`)
- **Gestão de Estado Complexa**: Abertura de nova aba para contornar limitações de iframes
- **Código Modular**: Separação clara entre configuração, utilitários, interação e lógica de negócio
- **Manutenibilidade**: Mapeamento dinâmico de XPaths e constantes centralizadas
- **Simulação Humana**: Pausas aleatórias entre ações para evitar detecção

---

## 🎬 Demonstração

### Fluxo de Execução

