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