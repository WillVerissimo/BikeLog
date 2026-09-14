const form = document.getElementById("loginForm");
const mensagem = document.getElementById("mensagem");

form.addEventListener("submit", async function(event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const senha = document.getElementById("senha").value;

    try {
        const resposta = await fetch("http://127.0.0.1:5000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email,
                senha
            })
        });

        const dados = await resposta.json();

        if (resposta.ok) {
            mensagem.textContent = dados.mensagem;
        } else {
            mensagem.textContent = dados.erro;
        }

    } catch (erro) {
        mensagem.textContent = "Não foi possível conectar ao servidor.";
    }
});