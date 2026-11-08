const listaPedaladas = document.getElementById("listaPedaladas");
const formPedalada = document.getElementById("formPedalada");
const mensagemPedalada = document.getElementById("mensagemPedalada");
const seletorBicicleta = document.getElementById("pedalBicicleta");
const cancelarPedalada = document.getElementById("cancelarPedalada");
let pedaladaEditando = null;

async function requisicaoPedal(url, options = {}) {
    const resposta = await fetch(API_URL + url, { credentials: "include", ...options });
    if (resposta.status === 401) {
        window.location.href = "login.html";
        throw new Error("Sessão encerrada.");
    }
    const dados = await resposta.json();
    if (!resposta.ok) throw new Error(dados.erro || "Erro na operação.");
    return dados;
}

async function atualizarBicicletasPedal() {
    const bicicletas = await requisicaoPed("/bicicletas");
    const atual = seletorBicicleta.value;
    seletorBicicleta.replaceChildren();
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Selecione sua bicicleta";
    seletorBicicleta.appendChild(placeholder);
    bicicletas.forEach(b => {
        const option = document.createElement("option");
        option.value = b.id;
        option.textContent = b.nome;
        seletorBicicleta.appendChild(option);
    });
    if (bicicletas.some(b => String(b.id) === atual)) seletorBicicleta.value = atual;
}

function zerarFormularioPedal() {
    pedaladaEditando = null;
    formPedalada.reset();
    document.getElementById("salvarPedalada").textContent = "Registrar pedalada";
    cancelarPedalada.hidden = true;
}

function prepararEdicaoPedal(p) {
    pedaladaEditando = p.id;
    seletorBicicleta.value = p.bicicleta_id;
    document.getElementById("pedalData").value = p.data;
    document.getElementById("pedalDistancia").value = p.distancia_km;
    document.getElementById("pedalDuracao").value = p.duracao_minutos;
    document.getElementById("pedalObservacoes").value = p.observacoes || "";
    document.getElementById("salvarPedalada").textContent = "Salvar alterações";
    cancelarPedalada.hidden = false;
    formPedalada.scrollIntoView({behavior:"smooth",block:"center"});
}

cancelarPedalada.addEventListener("click", zerarFormularioPedal);

async function carregarPedaladas() {
    const pedais = await requisicaoPed("/pedaladas");
    listaPedaladas.replaceChildren();
    const distancia = pedais.reduce((s,p) => s + Number(p.distancia_km), 0);
    const minutos = pedais.reduce((s,p) => s + Number(p.duracao_minutos), 0);
    const media = minutos ? distancia / (minutos / 60) : 0;
    document.getElementById("estatisticasPedais").textContent =
        `${pedais.length} pedais | ${distancia.toFixed(1)} km | ${(minutos/60).toFixed(1)} h | Média ${media.toFixed(1)} km/h`;
    if (!pedais.length) {
        listaPedaladas.textContent = "Nenhuma pedalada registrada.";
        return;
    }
    pedais.forEach(p => {
        const card = document.createElement("div");
        card.className = "bicicleta-card";
        const titulo = document.createElement("h3");
        titulo.textContent = `${p.data} — ${p.bicicleta_nome}`;
        const detalhes = document.createElement("p");
        detalhes.textContent = `${p.distancia_km} km | ${p.duracao_minutos} min | ${p.velocidade_media} km/h` + (p.observacoes ? ` | ${p.observacoes}` : "");
        const acoes = document.createElement("div");
        acoes.className = "bicicleta-acoes";
        const editar = document.createElement("button");
        editar.type = "button"; editar.textContent = "Editar";
        editar.className = "btn-editar";
        editar.addEventListener("click", () => prepararEdicaoPedal(p));
        const excluir = document.createElement("button");
        excluir.type = "button"; excluir.textContent = "Excluir";
        excluir.className = "btn-excluir";
        excluir.addEventListener("click", async () => {
            if (!confirm("Excluir esta pedalada?")) return;
            try {
                await requisicaoPed("/pedaladas/" + p.id, {method:"DELETE"});
                if (pedaladaEditando === p.id) zerarFormularioPedal();
                await carregarPedaladas();
                mensagemPedalada.textContent = "Pedalada excluída.";
            } catch(e) { mensagemPedalada.textContent = e.message; }
        });
        acoes.append(editar, excluir);
        card.append(titulo, detalhes, acoes);
        listaPedaladas.appendChild(card);
    });
}

formPedalada.addEventListener("submit", async e => {
    e.preventDefault();
    const dados = {
        bicicleta_id: Number(seletorBicicleta.value),
        data: document.getElementById("pedalData").value,
        distancia_km: Number(document.getElementById("pedalDistancia").value),
        duracao_minutos: Number(document.getElementById("pedalDuracao").value),
        observacoes: document.getElementById("pedalObservacoes").value
    };
    const editando = pedaladaEditando !== null;
    const botao = document.getElementById("salvarPedalada");
    botao.disabled = true;
    try {
        await requisicaoPed(editando ? "/pedaladas/" + pedaladaEditando : "/pedaladas", {
            method: editando ? "PUT" : "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify(dados)
        });
        zerarFormularioPedal();
        await carregarPedaladas();
        mensagemPedalada.textContent = editando ? "Pedalada atualizada!" : "Pedalada cadastrada!";
    } catch (erro) { mensagemPedalada.textContent = erro.message; }
    finally { botao.disabled = false; }
});

async function iniciarPedaladas() {
    try {
        await atualizarBicicletasPedal();
        await carregarPedaladas();
    } catch(e) {
        mensagemPedalada.textContent = "Erro ao carregar pedaladas: " + e.message;
    }
}
iniciarPedaladas();
