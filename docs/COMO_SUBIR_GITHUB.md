# Como concluir o envio para o GitHub

Este guia corresponde ao repositório que ja foi criado:

**https://github.com/Guilheme-collab/AED---NILSON**

A branch principal e `main`. O repositorio remoto ja possui um primeiro commit com README, `.gitignore`, firmware-fonte, resumo dos ensaios, documentos de encaminhamento e o projeto Proteus. Portanto, **nao execute `git init` nem `git remote add` novamente**. O procedimento correto e clonar o repositorio existente, copiar os arquivos completos deste pacote para a pasta clonada e fazer um novo commit.

## 1. Baixar e extrair o pacote

Baixe `Repositorio_GitHub_Nyquist_Engenharia_Computacao.zip` e extraia. A pasta interna chama-se `Entrega_EC_Nyquist`.

Exemplo de organizacao:

```text
C:\Projetos\
    Entrega_EC_Nyquist\    <- pasta extraida do ZIP
    AED---NILSON\          <- sera criada pelo git clone
```

## 2. Abrir o PowerShell na pasta que contem as duas pastas

No exemplo acima, abra o PowerShell em `C:\Projetos`.

Confirme que o Git esta instalado:

```powershell
git --version
```

Se nao estiver instalado, use https://git-scm.com/download/win e abra um terminal novo depois da instalacao.

## 3. Clonar o repositorio existente

Execute:

```powershell
git clone https://github.com/Guilheme-collab/AED---NILSON.git AED---NILSON
```

Isso cria a pasta `AED---NILSON` ja conectada ao GitHub e com o historico/arquivos que ja foram publicados.

## 4. Copiar o pacote completo para dentro da pasta clonada

Ainda em `C:\Projetos`, execute:

```powershell
robocopy "C:\Projetos\Entrega_EC_Nyquist" "C:\Projetos\AED---NILSON" /E
```

Troque `C:\Projetos` pelo caminho real onde voce extraiu o ZIP.

O comando copia as pastas e arquivos do pacote completo para o clone. Ele nao apaga a pasta `.git` que foi criada pelo `git clone`, pois ela existe somente no destino.

## 5. Validar os arquivos antes do commit

Entre na pasta clonada:

```powershell
cd C:\Projetos\AED---NILSON
```

Rode o verificador incluido no pacote:

```powershell
python scripts/validar_entrega.py
```

O script verifica a estrutura da entrega, os dez CSVs, os atrasos registrados, o formato/checksums do HEX e os arquivos internos do projeto Proteus. Ele nao compila o firmware nem executa a simulacao no Proteus.

Confira o que sera enviado:

```powershell
git status --short
```

Voce deve ver arquivos novos em `docs`, `dados/csv`, `figuras`, `scripts`, alem de PDF/DOCX de repasse, evidencias e o HEX. Os arquivos que ja estavam no repositorio remoto e nao mudaram nao aparecerao como novos.

## 6. Criar o commit e enviar

```powershell
git add -A
git status
git commit -m "feat(ec): completa firmware, dados e evidencias"
git push origin main
```

Na primeira autenticacao, o Git Credential Manager pode abrir o navegador para confirmar seu login no GitHub. Nao cole senha ou token no codigo, em arquivos do projeto ou na conversa.

## 7. Conferir a publicacao

Abra:

https://github.com/Guilheme-collab/AED---NILSON

Confira se aparecem as pastas `firmware`, `proteus`, `dados`, `figuras`, `scripts` e `docs`, incluindo os CSVs, HEX, PDF de evidencias e documento de repasse.

No terminal, tambem pode confirmar:

```powershell
git status
git log -1 --oneline
git remote -v
```

O estado esperado depois do envio e `nothing to commit, working tree clean`.

## 8. Atualizacoes futuras

Depois de alterar firmware, dados ou documentos:

```powershell
git add -A
git status
git commit -m "docs(ec): atualiza resultados e evidencias"
git push
```

Sempre mantenha o `.ino` e o `.hex` da mesma compilacao juntos. O HEX que veio no pacote teve seus registros e checksums Intel HEX verificados; essa verificacao estrutural nao prova sozinho que ele foi compilado exatamente a partir do `.ino` que esta na pasta. Se recompilar no Arduino IDE, substitua o HEX pelo novo e mantenha a fonte correspondente.

## 9. Alternativa com Git no WSL/Ubuntu

Se preferir usar o Ubuntu do WSL, navegue ate a pasta que contem `Entrega_EC_Nyquist` e use:

```bash
git clone https://github.com/Guilheme-collab/AED---NILSON.git AED---NILSON
cp -a Entrega_EC_Nyquist/. AED---NILSON/
cd AED---NILSON
python3 scripts/validar_entrega.py
git add -A
git status
git commit -m "feat(ec): completa firmware, dados e evidencias"
git push origin main
```

## Escopo deste repositorio

O repositorio documenta a contribuicao pratica da Engenharia da Computacao: firmware PI (Kp=1,40; Ki=1,00; Kd=0), co-simulacao Arduino/RC no Proteus, atraso de realimentacao implementado por buffer circular em software e dados dos dez ensaios.

Ele nao substitui os algoritmos gerais de Nyquist/winding number, Routh-Hurwitz, Lugar das Raizes, Bode, os quatro benchmarks A-D ou o benchmarking para ordens n=5, 10 e 20. Esses itens devem ficar com o integrante/equipe responsavel pelo nucleo computacional geral. A simulacao atual e co-simulacao no Proteus, nao HIL fisico com planta externa e comunicacao fisica real.
