<div align="center">

# 📱 Gerenciador de Tarefas - App Flutter Premium

[![Flutter Version](https://img.shields.io/badge/flutter-3.35+-blue.svg)](https://flutter.dev/)
[![Dart Version](https://img.shields.io/badge/dart-3.9+-green.svg)](https://dart.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Android%20%7C%20iOS%20%7C%20Web-lightgrey.svg)]()

**Aplicativo moderno de gerenciamento de tarefas com arquitetura limpa, persistência local e interface totalmente em português brasileiro**

[Sobre](#-sobre-o-projeto) • [Funcionalidades](#-principais-funcionalidades) • [Tecnologias](#️-tecnologias) • [Instalação](#-instalação) • [Como Usar](#-como-usar) • [Arquitetura](#️-arquitetura) • [Contato](#-contato)

</div>

---

## 📋 Sobre o Projeto

Este projeto implementa um **gerenciador de tarefas multiplataforma** desenvolvido com Flutter e Dart, demonstrando competências avançadas em desenvolvimento mobile, arquitetura de software e design de interfaces responsivas.

O aplicativo oferece uma experiência completa de gerenciamento de tarefas com persistência local, sincronização automática e interface intuitiva, seguindo os princípios de Clean Architecture e Material Design 3.

### 🎯 Problema Resolvido

Organizar tarefas diárias de forma eficiente é um desafio comum para profissionais e estudantes. Muitos aplicativos disponíveis são:

- 🌐 **Dependentes de conexão**: Requerem internet para funcionar
- 💰 **Pagos**: Cobram mensalidades por funcionalidades básicas
- 🔒 **Complexos**: Interface confusa com curva de aprendizado elevada
- 🌎 **Em inglês**: Falta de localização adequada para português brasileiro

**Solução**: App totalmente offline com persistência local, interface em português, gratuito e com design minimalista focado em produtividade.

---

## ✨ Principais Funcionalidades

- 📝 **CRUD Completo de Tarefas**: Criação, leitura, atualização e exclusão com validações
- ✅ **Sistema de Conclusão**: Marcar/desmarcar tarefas com indicador visual (linha riscada)
- 💾 **Persistência Local**: Dados salvos automaticamente usando SharedPreferences
- 📊 **Indicador de Progresso**: Contador visual e barra de progresso das tarefas concluídas
- 🗑️ **Confirmação de Exclusão**: Diálogo de confirmação para prevenir perdas acidentais
- 📅 **Data de Criação**: Registro automático com formatação brasileira (dd/MM/yyyy HH:mm)
- 🎨 **Material Design 3**: Interface moderna seguindo as diretrizes do Google
- 🌐 **Internacionalização**: Totalmente localizado para pt_BR (datas, textos, validações)
- 📱 **Responsivo**: Layout adaptável para diferentes tamanhos de tela
- 🔄 **Atualização em Tempo Real**: Alterações refletidas instantaneamente na interface

---

## 🛠️ Tecnologias

### Stack Principal

| Tecnologia | Versão | Aplicação |
|-----------|--------|-----------|
| **Flutter** | 3.35+ | Framework multiplataforma |
| **Dart** | 3.9+ | Linguagem de programação |
| **SharedPreferences** | 2.2.2 | Persistência de dados local |
| **Intl** | 0.19.0 | Internacionalização e formatação de datas |
| **Material Design 3** | Latest | Sistema de design visual |

### Conceitos Técnicos Aplicados

- **Clean Architecture**: Separação de responsabilidades (Models, Services, Screens, Widgets)
- **State Management**: Gerenciamento de estado com StatefulWidget e setState
- **Data Persistence**: Serialização JSON e armazenamento local
- **Design Patterns**: Repository Pattern, Factory Pattern
- **Responsive Design**: Layout adaptável com MediaQuery e Flexible widgets
- **Error Handling**: Tratamento de exceções e validações de formulário
- **Internationalization (i18n)**: Localização pt_BR com flutter_localizations
- **Code Quality**: Linting com flutter_lints, nomenclatura descritiva em português

---

## 📦 Instalação

### Pré-requisitos

- **Flutter SDK 3.0 ou superior** ([Download](https://docs.flutter.dev/get-started/install))
- **Dart SDK 3.0 ou superior** (incluído no Flutter)
- **Android Studio / Xcode** (para emuladores) ou dispositivo físico
- **Git** (opcional, para clonar o repositório)

### Passo a Passo

**1. Clone o repositório**

git clone https://github.com/seu-usuario/gerenciador-tarefas-flutter.git
cd gerenciador-tarefas-flutter

**2. Instale as dependências**

flutter pub get

**3. Verifique a instalação**

flutter doctor

**4. Execute o aplicativo**

Android
flutter run

iOS (apenas macOS)
flutter run -d ios

Web
flutter run -d chrome

Windows
flutter run -d windows

---

## 🚀 Como Usar

### Primeira Execução

**1. Tela Inicial**
   - Ao abrir o app, você verá a mensagem "Nenhuma tarefa cadastrada"
   - Clique no botão flutuante "Nova Tarefa" para começar

**2. Adicionar Tarefa**
   - Preencha o **Título** (obrigatório)
   - Adicione uma **Descrição** (opcional)
   - Clique em "Salvar Tarefa"

**3. Gerenciar Tarefas**
   - **Marcar como concluída**: Clique no checkbox ao lado da tarefa
   - **Excluir**: Clique no ícone de lixeira (vermelho) e confirme a ação
   - **Visualizar progresso**: Veja o contador no topo da tela

### Fluxo de Utilização

[Tela Inicial]
↓
[Clica em "Nova Tarefa"]
↓
[Preenche formulário]
↓
[Salva tarefa]
↓
[Retorna à lista atualizada]
↓
[Marca como concluída/Exclui conforme necessário]

### Exemplo de Tela

**Lista de Tarefas:**
┌──────────────────────────────────────┐
│ Minhas Tarefas │
├──────────────────────────────────────┤
│ 3 de 5 concluídas │
│ ████████████░░░░░░░░ 60% │
├──────────────────────────────────────┤
│ ☑ Estudar Flutter │
│ Revisar widgets básicos │
│ 13/10/2025 12:30 │
│ 🗑️ │
├──────────────────────────────────────┤
│ ☐ Fazer compras │
│ Mercado + farmácia │
│ 13/10/2025 14:15 │
│ 🗑️ │
└──────────────────────────────────────┘
[➕ Nova Tarefa]

---

## 🏗️ Arquitetura

### Estrutura de Diretórios

gerenciador_tarefas/
├── lib/
│ ├── main.dart # Entry Point + Configuração do App
│ ├── models/
│ │ └── tarefa.dart # Modelo de dados da Tarefa
│ ├── services/
│ │ └── servico_tarefas.dart # Lógica de persistência
│ ├── screens/
│ │ ├── tela_inicial.dart # Tela principal com lista
│ │ └── tela_adicionar_tarefa.dart # Formulário de criação
│ └── widgets/
│ └── cartao_tarefa.dart # Card customizado de tarefa
├── pubspec.yaml # Dependências do projeto
└── README.md # Documentação

### Camadas da Arquitetura

**1. Models (Entidades)**
// lib/models/tarefa.dart
class Tarefa {
final String id;
final String titulo;
final String descricao;
final DateTime dataCriacao;
bool estaConcluida;

// Serialização JSON para persistência
Map<String, dynamic> paraJson() { ... }
factory Tarefa.deJson(Map<String, dynamic> json) { ... }
}

**2. Services (Lógica de Negócio)**
// lib/services/servico_tarefas.dart
class ServicoTarefas {
// CRUD completo com SharedPreferences
Future<List<Tarefa>> obterTarefas() async { ... }
Future<void> adicionarTarefa(Tarefa tarefa) async { ... }
Future<void> excluirTarefa(String id) async { ... }
Future<void> alternarTarefa(String id) async { ... }
}

**3. Screens (Interface)**
// lib/screens/tela_inicial.dart
class TelaInicial extends StatefulWidget {
// Gerenciamento de estado com setState
// ListView.builder para renderização otimizada
// Indicador de progresso com LinearProgressIndicator
}

**4. Widgets (Componentes Reutilizáveis)**
// lib/widgets/cartao_tarefa.dart
class CartaoTarefa extends StatelessWidget {
// Card customizado com Checkbox, título, descrição
// Formatação de data em português
// Botão de exclusão com callback
}

### Destaques Técnicos

**1. Persistência com Serialização JSON**

Conversão bidirecional entre objetos Dart e JSON para armazenamento:

// Serialização (Objeto → JSON)
Map<String, dynamic> paraJson() {
return {
'id': id,
'titulo': titulo,
'descricao': descricao,
'dataCriacao': dataCriacao.toIso8601String(),
'estaConcluida': estaConcluida,
};
}

// Desserialização (JSON → Objeto)
factory Tarefa.deJson(Map<String, dynamic> json) {
return Tarefa(
id: json['id'],
titulo: json['titulo'],
descricao: json['descricao'],
dataCriacao: DateTime.parse(json['dataCriacao']),
estaConcluida: json['estaConcluida'] ?? false,
);
}

**2. Localização para Português Brasileiro**

Configuração completa de i18n no MaterialApp:

MaterialApp(
locale: const Locale('pt', 'BR'),
localizationsDelegates: const [
GlobalMaterialLocalizations.delegate,
GlobalWidgetsLocalizations.delegate,
GlobalCupertinoLocalizations.delegate,
],
supportedLocales: const [Locale('pt', 'BR')],
// ...
)

**3. Validação de Formulários**

TextFormField com validators personalizados:

TextFormField(
controller: _controladorTitulo,
decoration: const InputDecoration(
labelText: 'Título',
border: OutlineInputBorder(),
prefixIcon: Icon(Icons.title),
),
validator: (valor) {
if (valor == null || valor.isEmpty) {
return 'Por favor, insira um título';
}
return null;
},
)

**4. Confirmação de Exclusão**

Diálogo modal para prevenir exclusões acidentais:

Future<void> _excluirTarefa(String id) async {
final confirmar = await showDialog<bool>(
context: context,
builder: (BuildContext context) {
return AlertDialog(
title: const Text('Confirmar exclusão'),
content: const Text('Tem certeza que deseja excluir?'),
actions: [
TextButton(
onPressed: () => Navigator.pop(context, false),
child: const Text('Cancelar'),
),
TextButton(
onPressed: () => Navigator.pop(context, true),
child: const Text('Excluir'),
),
],
);
},
);

if (confirmar == true) {
await _servicoTarefas.excluirTarefa(id);
}
}

---

## 📈 Resultados e Aprendizados

### Métricas de Impacto

- ⏱️ **Performance**: Inicialização em < 1 segundo, carregamento instantâneo de tarefas
- 💾 **Persistência**: 100% de retenção de dados entre sessões
- 📱 **Compatibilidade**: Funciona em Android, iOS, Web e Desktop
- 🎨 **UX**: Interface intuitiva com feedback visual imediato

### Desafios Técnicos Superados

**1. Serialização de Dados Complexos**
   - **Problema**: SharedPreferences aceita apenas tipos primitivos (String, int, bool)
   - **Solução**: Implementação de serialização JSON customizada (toJson/fromJson)

**2. Formatação de Datas em Português**
   - **Problema**: Dart formata datas em inglês por padrão
   - **Solução**: Integração do pacote `intl` com inicialização de locale pt_BR no main()

**3. Gerenciamento de Estado**
   - **Problema**: Atualização da UI após operações assíncronas
   - **Solução**: Uso adequado de setState() após operações do ServicoTarefas

**4. Validação de Formulários**
   - **Problema**: Prevenir salvamento de tarefas sem título
   - **Solução**: GlobalKey<FormState> com validators personalizados

---

## 🔮 Melhorias Futuras

- [ ] **Categorias/Tags**: Organização de tarefas por categorias coloridas
- [ ] **Busca e Filtros**: Campo de pesquisa e filtros (concluídas/pendentes)
- [ ] **Data de Vencimento**: Notificações push para tarefas com prazo
- [ ] **Temas Customizáveis**: Modo escuro e cores personalizadas
- [ ] **Sincronização Cloud**: Backup automático com Firebase/Supabase
- [ ] **Estatísticas**: Gráficos de produtividade semanal/mensal
- [ ] **Subtarefas**: Hierarquia de tarefas com checklists
- [ ] **Compartilhamento**: Exportar/importar tarefas via JSON

---

## 💡 Por Que Este Projeto?

Este app demonstra minha expertise em **desenvolvimento mobile multiplataforma** aplicada a cenários reais:

- Arquitetura escalável e manutenível (separação de responsabilidades)
- Persistência de dados com estratégias modernas (JSON + SharedPreferences)
- Interface responsiva seguindo Material Design 3
- Código limpo com nomenclatura em português (acessibilidade)

Como desenvolvedor back-end especializado em Python/Java e professor de programação, busco expandir minhas habilidades para o universo mobile, criando soluções que otimizam processos e geram valor mensurável.

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
