# Desenvolvimento e manutenção

## Fluxo de uma alteração

1. Escolha um problema ou funcionalidade concreta e crie uma branch com nome descritivo.
2. Mantenha arquivos da mesma funcionalidade próximos, respeitando a organização descrita em [docs/REVISAO.md](docs/REVISAO.md).
3. Para regras ou correções de comportamento, adicione um teste que falhe antes da correção. Use substitutos para serviços externos nos testes unitários.
4. Execute as verificações aplicáveis e descreva no PR o que mudou, por quê e o que não foi possível executar.
5. Atualize o README quando mudar setup, comandos ou funcionalidades. Revise o diff antes do merge e preserve atribuições e licença.

## Comandos

```sh
python -m unittest discover -s tests -v
```

## Rotina sugerida

- A cada mudança: executar os testes relacionados e conferir o resultado da CI.
- Mensalmente, ou antes de retomar um projeto parado: revisar dependências, avisos de segurança e instruções de instalação. Atualizar dependências em mudanças pequenas, verificando compatibilidade; não atualizar apenas para produzir commits.
- Ao estudar uma técnica: usar uma POC separada e registrar a conclusão antes de migrar código estável.
- Ao concluir uma funcionalidade: documentar o comportamento real e remover promessas ou links que ainda não têm implementação.

Essa é uma rotina de trabalho manual, não uma automação agendada. Não publicar segredos, arquivos `.env`, caches ou dependências instaladas. A tecnologia e a arquitetura devem servir ao tamanho do projeto.
