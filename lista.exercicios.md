# Exercícios - Estrutura de Decisão

## 📋 Exercício 1: Classificador de Idade

### Contexto
Criar sistema de classificação etária para cinema/jogos.

### Objetivo
Classificar pessoa em categorias baseado na idade.

### Checklist
- [ ] Solicitar idade do usuário
- [ ] Classificar: Criança (0-12), Adolescente (13-17), Adulto (18-59), Idoso (60+)
- [ ] Validar se idade é positiva
- [ ] Informar benefícios da categoria (desconto, gratuidade)
- [ ] Verificar se pode assistir filme 18+
- [ ] Usar if/elif/else adequadamente

### Saída Esperada
```
=== CLASSIFICAÇÃO ETÁRIA ===
Idade: 15

Categoria: Adolescente
Benefícios: Meia-entrada em cinemas
Restrições: Filmes 18+ proibidos
Pode entrar sozinho: Não (precisa acompanhante)
```

---

## 📋 Exercício 2: Calculadora de Multas de Trânsito

### Contexto
Sistema para calcular multa baseada na velocidade do veículo.

### Objetivo
Determinar tipo de multa e pontos na CNH conforme excesso de velocidade.

### Checklist
- [ ] Solicitar velocidade permitida na via
- [ ] Solicitar velocidade do veículo
- [ ] Calcular excesso de velocidade
- [ ] Classificar infração: Leve (até 20%), Média (20-50%), Grave (50%+)
- [ ] Definir valor da multa: Leve (R$ 130), Média (R$ 195), Grave (R$ 880)
- [ ] Definir pontos na CNH: Leve (3), Média (5), Grave (7)
- [ ] Verificar suspensão se velocidade > 50% do limite

### Saída Esperada
```
=== MULTA DE TRÂNSITO ===
Limite: 60 km/h
Velocidade: 85 km/h
Excesso: 25 km/h (41.67%)

INFRAÇÃO: Média
Valor da multa: R$ 195.00
Pontos na CNH: 5 pontos
Status: Multa aplicada
```

---

## 📋 Exercício 3: Sistema de Login com Tentativas

### Contexto
Implementar sistema de autenticação com limite de tentativas.

### Objetivo
Validar usuário e senha com segurança.

### Checklist
- [ ] Definir usuário e senha corretos
- [ ] Solicitar credenciais do usuário
- [ ] Verificar se usuário existe
- [ ] Verificar se senha está correta
- [ ] Controlar número de tentativas (máximo 3)
- [ ] Bloquear após 3 tentativas falhas
- [ ] Diferenciar erro de usuário vs senha
- [ ] Usar operadores lógicos (and/or)

### Saída Esperada
```
=== SISTEMA DE LOGIN ===
Usuário: joao123
Senha: ********

❌ Senha incorreta
Tentativas restantes: 2

[Segunda tentativa]
✅ Login realizado com sucesso!
Bem-vindo, João Silva!
```

---
