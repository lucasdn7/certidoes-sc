

## Fluxo híbrido com CAPTCHA e certificado

Na tela de resultados, documentos que não puderem ser baixados automaticamente terão os botões **Abrir portal oficial** e **Anexar PDF emitido**. O botão do portal copia o CNPJ e abre o endereço oficial em uma nova aba. Depois de resolver CAPTCHA, fazer login ou usar certificado digital no portal do órgão, baixe o PDF e volte à aplicação para anexá-lo.

O formulário de anexação valida o tipo PDF e permite registrar número da certidão, data de emissão e validade em dias. O status fica como `REGISTRADA` e os metadados são guardados no navegador via `localStorage`, separados por documento e certidão. Nesta etapa, o PDF anexado permanece disponível somente na sessão atual do navegador; armazenamento permanente em Supabase Storage ou Vercel Blob deve ser configurado antes de uso institucional.
