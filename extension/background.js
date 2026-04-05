// Nome que você colocou no Registro do Windows e no host_manifest.json
const hostName = "com.hashed_maze";

// 1. Ouve as mensagens que vêm da página (do content.js)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    
    if (request.action === "get_pass") {
        console.log("Solicitando senha para:", request.url);

        // 2. Conecta com o seu programa Python (Native Messaging)
        chrome.runtime.sendNativeMessage(
            hostName,
            { action: "get", url: request.url },
            (response) => {
                if (chrome.runtime.lastError) {
                    console.error("Erro ao falar com Python:", chrome.runtime.lastError.message);
                    sendResponse({ password: "Connection error" });
                } else {
                    // 3. Devolve a senha que o Python achou para o content.js
                    sendResponse({ password: response.password });
                }
            }
        );
        return true; // Mantém o canal aberto para a resposta assíncrona
    }
});