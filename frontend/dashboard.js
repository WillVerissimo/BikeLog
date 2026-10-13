
const API_URL = "http://127.0.0.1:5000";

const boasVindas = document.getElementById("boasVindas");
const listaBicicletas = document.getElementById("listaBicicletas");
const formBicicleta = document.getElementById("formBicicleta");
const mensagemBicicleta = document.getElementById("mensagemBicicleta");

const btnLogout = document.getElementById("btnLogout");
const btnCadastrar = document.getElementById("btnCadastrar");
const btnCancelarEdicao = document.getElementById("btnCancelarEdicao");

let bicicletaEmEdicao = null;


// 1. VERIFICAR USUÁRIO LOGADO

async function verificarUsuario() {
    const resposta = await fetch(`${API_URL}/me`, {
        credentials: "include"
    });

    if (resposta.status === 401) {
        window.location.href = "login.html";
        return false;
    }

    if (!resposta.ok) {
        throw new Error("Erro ao verificar usuário.");
    }

    const usuario = await resposta.json();

    boasVindas.textContent = `Bem-vindo, ${usuario.nome}!`;

    return true;
}


// 2. LISTAR BICICLETAS

async function carregarBicicletas() {
    const resposta = await fetch(`${API_URL}/bicicletas`, {
        credentials: "include"
    });

    if (resposta.status === 401) {
        window.location.href = "login.html";
        return;
    }

    if (!resposta.ok) {
        throw new Error("Erro ao carregar bicicletas.");
    }

    const bicicletas = await resposta.json();

    listaBicicletas.replaceChildren();

    if (bicicletas.length === 0) {
        const aviso = document.createElement("p");
        aviso.textContent = "Nenhuma bicicleta cadastrada.";
        listaBicicletas.appendChild(aviso);
        return;
    }

    bicicletas.forEach(bicicleta => {
        const card = document.createElement("div");
        card.className = "bicicleta-card";

        const nome = document.createElement("h3");
        nome.textContent = bicicleta.nome;

        const detalhes = document.createElement("p");
        detalhes.textContent =
            `${bicicleta.marca || "Sem marca"} - ` +
            `${bicicleta.modelo || "Sem modelo"} - ` +
            `${bicicleta.tipo || "Sem tipo"}`;

        const acoes = document.createElement("div");
        acoes.className = "bicicleta-acoes";

        // BOTÃO EDITAR

        const btnEditar = document.createElement("button");
        btnEditar.type = "button";
        btnEditar.textContent = "Editar";
        btnEditar.className = "btn-editar";

        btnEditar.addEventListener("click", () => {
            prepararEdicao(bicicleta);
        });

        // BOTÃO EXCLUIR

        const btnExcluir = document.createElement("button");
        btnExcluir.type = "button";
        btnExcluir.textContent = "Excluir";
        btnExcluir.className = "btn-excluir";

        btnExcluir.addEventListener("click", () => {
            excluirBicicleta(bicicleta.id);
        });

        acoes.appendChild(btnEditar);
        acoes.appendChild(btnExcluir);

        card.appendChild(nome);
        card.appendChild(detalhes);
        card.appendChild(acoes);

        listaBicicletas.appendChild(card);
    });
}


// 3. PREPARAR EDIÇÃO

function prepararEdicao(bicicleta) {
    bicicletaEmEdicao = bicicleta.id;

    document.getElementById("nomeBicicleta").value =
        bicicleta.nome;

    document.getElementById("marca").value =
        bicicleta.marca || "";

    document.getElementById("modelo").value =
        bicicleta.modelo || "";

    document.getElementById("tipo").value =
        bicicleta.tipo || "";

    btnCadastrar.textContent = "Salvar alterações";
    btnCancelarEdicao.hidden = false;

    mensagemBicicleta.textContent =
        `Editando: ${bicicleta.nome}`;

    formBicicleta.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


// 4. CANCELAR EDIÇÃO

function cancelarEdicao() {
    bicicletaEmEdicao = null;

    formBicicleta.reset();

    btnCadastrar.textContent = "Cadastrar bicicleta";
    btnCancelarEdicao.hidden = true;

    mensagemBicicleta.textContent = "";
}

btnCancelarEdicao.addEventListener("click", cancelarEdicao);


// 5. CADASTRAR OU EDITAR

formBicicleta.addEventListener("submit", async function(event) {
    event.preventDefault();

    const dados = {
        nome: document.getElementById("nomeBicicleta").value,
        marca: document.getElementById("marca").value,
        modelo: document.getElementById("modelo").value,
        tipo: document.getElementById("tipo").value
    };

    const editando = bicicletaEmEdicao !== null;

    const url = editando
        ? `${API_URL}/bicicletas/${bicicletaEmEdicao}`
        : `${API_URL}/bicicletas`;

    const metodo = editando ? "PUT" : "POST";

    btnCadastrar.disabled = true;
    btnCancelarEdicao.disabled = true;

    try {
        const resposta = await fetch(url, {
            method: metodo,
            credentials: "include",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(dados)
        });

        if (resposta.status === 401) {
            window.location.href = "login.html";
            return;
        }

        const resultado = await resposta.json();

        if (!resposta.ok) {
            mensagemBicicleta.textContent =
                resultado.erro || "Erro ao salvar bicicleta.";
            return;
        }

        cancelarEdicao();

        await carregarBicicletas();

        mensagemBicicleta.textContent = editando
            ? "Bicicleta atualizada com sucesso!"
            : "Bicicleta cadastrada com sucesso!";

    } catch (erro) {
        mensagemBicicleta.textContent =
            "Não foi possível concluir a operação.";
        console.error(erro);

    } finally {
        btnCadastrar.disabled = false;
        btnCancelarEdicao.disabled = false;
    }
});


// 6. EXCLUIR BICICLETA

async function excluirBicicleta(id) {
    const confirmar = confirm(
        "Tem certeza que deseja excluir esta bicicleta?"
    );

    if (!confirmar) {
        return;
    }

    try {
        const resposta = await fetch(
            `${API_URL}/bicicletas/${id}`,
            {
                method: "DELETE",
                credentials: "include"
            }
        );

        if (resposta.status === 401) {
            window.location.href = "login.html";
            return;
        }

        const resultado = await resposta.json();

        if (!resposta.ok) {
            alert(resultado.erro || "Erro ao excluir bicicleta.");
            return;
        }

        if (bicicletaEmEdicao === id) {
            cancelarEdicao();
        }

        await carregarBicicletas();

        mensagemBicicleta.textContent =
            "Bicicleta excluída com sucesso!";

    } catch (erro) {
        alert("Não foi possível excluir a bicicleta.");
        console.error(erro);
    }
}


// 7. LOGOUT

btnLogout.addEventListener("click", async function() {
    try {
        const resposta = await fetch(`${API_URL}/logout`, {
            method: "POST",
            credentials: "include"
        });

        if (!resposta.ok) {
            throw new Error("Erro no logout.");
        }

        window.location.href = "login.html";

    } catch (erro) {
        alert("Não foi possível encerrar a sessão.");
        console.error(erro);
    }
});


// 8. INICIAR DASHBOARD

async function iniciarDashboard() {
    try {
        const autenticado = await verificarUsuario();

        if (autenticado) {
            await carregarBicicletas();
        }

    } catch (erro) {
        listaBicicletas.textContent =
            "Erro ao carregar os dados. Verifique o servidor.";

        console.error(erro);
    }
}

iniciarDashboard();
