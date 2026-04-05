document.addEventListener('focusin', (e) => {
    if (e.target.type !== 'password') return;

    const campo = e.target;
    const urlCompleta = window.location.href;

    // 1. Pequeno atraso para garantir que o clique/foco do usuário terminou
    setTimeout(() => {
        console.log("[HashedMaze] Disparando busca para:", urlCompleta);
        
        chrome.runtime.sendMessage({ action: "get_pass", url: urlCompleta }, (response) => {
            if (chrome.runtime.lastError) {
                console.error("[HashedMaze] Erro no canal:", chrome.runtime.lastError.message);
                return;
            }

            if (response && response.password && response.password !== "Não encontrada") {
                // 2. O segredo: Limpa o campo e foca antes de atribuir o valor
                campo.value = ""; 
                campo.value = response.password;

                // 3. Notifica o site de que o valor mudou (essencial para sites modernos)
                const eventos = ['input', 'change', 'keydown', 'keyup', 'blur'];
                eventos.forEach(nome => {
                    campo.dispatchEvent(new Event(nome, { bubbles: true }));
                });
                
                console.log("[HashedMaze] Campo preenchido.");
            }
        });
    }, 150); // 150ms é o "tempo humano" ideal para o navegador processar o foco
});

// document.addEventListener('focusin', (e) => {
//     // 1. Filtro rigoroso: só campos de senha
//     if (e.target.tagName !== 'INPUT' || e.target.type !== 'password') return;
    
//     const campo = e.target;
    
//     // Pequeno delay de 100ms para garantir que o foco estabilizou no site
//     setTimeout(() => {
//         // Só tenta buscar se o campo estiver realmente vazio (para não irritar o usuário)
//         if (!campo.value || campo.value.trim() === "") {
//             solicitarSenha(campo);
//         }
//     }, 100);
// });

// function solicitarSenha(campo) {
//     if (!chrome.runtime?.id) return;

//     const url = window.location.href; // Usar hostname é mais preciso que a URL completa para o banco

//     chrome.runtime.sendMessage({ action: "get_pass", url: url }, (response) => {
//         if (chrome.runtime.lastError) {
//             console.error("[HashedMaze] Erro de conexão:", chrome.runtime.lastError.message);
//             return;
//         }

//         if (response && response.password && response.password !== "Não encontrada") {
//             preencherCampoComSeguranca(campo, response.password);
//         }
//     });
// }

// function preencherCampoComSeguranca(campo, senha) {
//     // 1. Define o valor diretamente
//     campo.value = senha;

//     // 2. Dispara a sequência de eventos que "engana" os frameworks (React/Vue)
//     // Isso simula que o usuário digitou e saiu do campo
//     const eventos = ['input', 'change', 'blur'];
//     eventos.forEach(nomeEvento => {
//         campo.dispatchEvent(new Event(nomeEvento, { bubbles: true }));
//     });

//     // 3. Força um estilo visual para você saber que a extensão atuou (Opcional)
//     campo.style.backgroundColor = "rgba(0, 255, 0, 0.05)"; 
//     setTimeout(() => campo.style.backgroundColor = "", 500);
// }

// INICIO ONDE TUDO AINDA FUNCIONA MESMO PRECARIAMENTE

// // Detecta quando você clica em QUALQUER campo de senha em QUALQUER site
// document.addEventListener('focusin', handlePasswordField);

// function handlePasswordField(e) {
//     if (e.target.type !== 'password') return;
//     if (!chrome.runtime?.id) return;

//     const url = window.location.href;
//     tryGetPassword(e.target, url);
// }

// function tryGetPassword(campo, url, tentativa = 1) {
//     if (!chrome.runtime?.id) return;

//     try {
//         chrome.runtime.sendMessage({ action: "get_pass", url: url }, (response) => {
//             if (chrome.runtime.lastError) {
//                 if (tentativa < 6) {
//                     setTimeout(() => tryGetPassword(campo, url, tentativa + 1), tentativa * 300);
//                 }
//                 return;
//             }

//             if (response?.password) {
//                 // Decide aqui se quer sempre sobrescrever ou só quando vazio
//                 if (!campo.value || campo.value.trim() === "") {
//                     campo.value = response.password;
//                     campo.dispatchEvent(new Event('input', { bubbles: true }));
//                     campo.dispatchEvent(new Event('change', { bubbles: true }));
//                 }
//             }
//         });
//     } catch (err) {
//         if (err.message?.includes('Extension context invalidated')) {
//             window.location.reload();
//             return;
//         }
//         console.error('[HashedMaze] Erro inesperado:', err);
//     }
// }


