let trabalhoCount = 0;
let ordemAscendente = true;

function mostrarFlash(mensagem, tipo) {
    const container = document.querySelector('.container');
    const flashDiv = document.createElement('div');
    flashDiv.className = `flash ${tipo}`;
    flashDiv.innerHTML = (tipo === 'success' ? '✅ ' : 'ℹ️ ') + mensagem;
    container.insertBefore(flashDiv, container.children[1]);
    setTimeout(() => flashDiv.remove(), 3000);
}

async function enviarAtualizacao(formData, nomeOriginal) {
    try {
        const response = await fetch('/atualizar_campo', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.status === 'success') {
            const somaSpan = document.getElementById(`soma-${nomeOriginal.replace(/ /g, '_')}`);
            if (somaSpan) somaSpan.textContent = data.nova_soma;
            return data;
        } else {
            alert('Erro: ' + data.message);
            return null;
        }
    } catch (error) {
        alert('Erro de conexão com o servidor.');
        console.error(error);
        return null;
    }
}

function addTrabalho() {
    trabalhoCount++;
    const container = document.getElementById('trabalhos-container');
    const div = document.createElement('div');
    div.className = 'trabalho-item';
    div.innerHTML = `
        <input type="number" step="0.1" min="0" max="10" name="trabalhos" 
               placeholder="Nota do Trabalho ${trabalhoCount}" required>
        <button type="button" class="btn btn-danger btn-sm btn-remover-trabalho" 
                style="padding: 12px;">❌</button>
    `;
    container.appendChild(div);
    div.querySelector('.btn-remover-trabalho').addEventListener('click', function() {
        this.parentElement.remove();
    });
}

async function editarCampo(nomeAluno, campo, valorAtual, indice = null) {
    let novoValor;

    if (campo === 'trabalho_adicionar') {
        novoValor = prompt('Nota do novo trabalho (0-10):');
        if (novoValor === null) return;
    } else if (campo === 'trabalho_editar') {
        novoValor = prompt('Nova nota do trabalho:', valorAtual);
        if (novoValor === null || novoValor === valorAtual) return;
    } else if (campo === 'trabalho_remover') {
        if (!confirm('Remover este trabalho?')) return;
        const formData = new FormData();
        formData.append('nome', nomeAluno);
        formData.append('campo', 'trabalho_remover');
        formData.append('indice', indice);
        const data = await enviarAtualizacao(formData, nomeAluno);
        if (data) window.location.reload();
        return;
    } else {
        novoValor = prompt(`Novo valor para ${campo}:`, valorAtual);
        if (novoValor === null || novoValor === valorAtual) return;
    }

    if (campo.includes('nota') || campo.includes('trabalho')) {
        const num = parseFloat(novoValor);
        if (isNaN(num) || num < 0 || num > 10) {
            alert('Valor deve ser um número entre 0 e 10.');
            return;
        }
        novoValor = num;
    } else {
        if (!novoValor.trim()) {
            alert('O valor não pode ser vazio.');
            return;
        }
        novoValor = novoValor.trim();
    }

    const formData = new FormData();
    formData.append('nome', nomeAluno);
    formData.append('campo', campo);
    formData.append('valor', novoValor);
    if (indice !== null) formData.append('indice', indice);

    const data = await enviarAtualizacao(formData, nomeAluno);
    if (!data) return;

    if (campo === 'nome') {
        window.location.reload();
        return;
    }

    const linha = document.querySelector(`tr[data-nome="${nomeAluno}"]`);
    if (!linha) return;

    if (campo === 'turma') {
        linha.querySelector('.turma-valor').textContent = novoValor;
        linha.querySelector('[data-campo="turma"]').dataset.valor = novoValor;
    } else if (campo === 'nota_discursiva') {
        linha.cells[2].querySelector('.nota-valor').textContent = novoValor;
        linha.querySelector('[data-campo="nota_discursiva"]').dataset.valor = novoValor;
    } else if (campo === 'nota_objetiva') {
        linha.cells[3].querySelector('.nota-valor').textContent = novoValor;
        linha.querySelector('[data-campo="nota_objetiva"]').dataset.valor = novoValor;
    } else if (campo === 'trabalho_adicionar' || campo === 'trabalho_editar') {
        window.location.reload();
        return;
    }

    mostrarFlash('Atualizado com sucesso!', 'success');
}

function ordenarTabela() {
    const tabela = document.getElementById('tabela-alunos');
    if (!tabela) return;
    const tbody = tabela.tBodies[0];
    const linhas = Array.from(tbody.rows);
    if (linhas.length === 0 || linhas[0].cells.length === 1) return;

    linhas.sort((a, b) => {
        const nomeA = a.cells[0].querySelector('.nome-valor').textContent.trim().toLowerCase();
        const nomeB = b.cells[0].querySelector('.nome-valor').textContent.trim().toLowerCase();
        return ordemAscendente ? nomeA.localeCompare(nomeB) : nomeB.localeCompare(nomeA);
    });

    linhas.forEach(linha => tbody.appendChild(linha));
    const icone = document.getElementById('ordem-icone');
    if (icone) icone.textContent = ordemAscendente ? '⬆️ A-Z' : '⬇️ Z-A';
    ordemAscendente = !ordemAscendente;
}

document.addEventListener('DOMContentLoaded', function() {
    const addBtn = document.getElementById('add-trabalho-btn');
    if (addBtn) addBtn.addEventListener('click', addTrabalho);

    document.body.addEventListener('click', function(e) {
        const editIcon = e.target.closest('[data-editar-campo]');
        if (editIcon) {
            const nome = editIcon.dataset.nome;
            const campo = editIcon.dataset.campo;
            const valor = editIcon.dataset.valor;
            editarCampo(nome, campo, valor);
            return;
        }

        const editTrab = e.target.closest('.edit-trabalho');
        if (editTrab) {
            const nome = editTrab.dataset.nome;
            const indice = editTrab.dataset.indice;
            const valor = editTrab.dataset.valor;
            editarCampo(nome, 'trabalho_editar', valor, indice);
            return;
        }

        const delTrab = e.target.closest('.delete-trabalho');
        if (delTrab) {
            const nome = delTrab.dataset.nome;
            const indice = delTrab.dataset.indice;
            editarCampo(nome, 'trabalho_remover', null, indice);
            return;
        }

        const addTrabBtn = e.target.closest('.btn-add-trabalho-inline');
        if (addTrabBtn) {
            const nome = addTrabBtn.dataset.nome;
            editarCampo(nome, 'trabalho_adicionar');
            return;
        }
    });

    document.querySelectorAll('.btn-remover-trabalho').forEach(btn => {
        btn.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });
});