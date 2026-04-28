from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'Tocbigor14'

ARQUIVO_JSON = 'alunos.json'

class Aluno:
    def __init__(self, nome, turma, nota_discursiva, nota_objetiva, trabalhos=None):
        self.nome = nome.strip()
        self.turma = turma.strip()
        self.nota_discursiva = float(nota_discursiva)
        self.nota_objetiva = float(nota_objetiva)
        self.trabalhos = [float(t) for t in trabalhos] if trabalhos else []
        self.soma = self.nota_discursiva + self.nota_objetiva + sum(self.trabalhos)

    def to_dict(self):
        return {
            'nome': self.nome,
            'turma': self.turma,
            'nota_discursiva': self.nota_discursiva,
            'nota_objetiva': self.nota_objetiva,
            'trabalhos': self.trabalhos,
            'soma': self.soma
        }

def carregar_alunos():
    if os.path.exists(ARQUIVO_JSON):
        with open(ARQUIVO_JSON, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            alunos = []
            for a in dados:
                a.pop('soma', None)
                alunos.append(Aluno(**a))
            return alunos
    return []

def salvar_alunos(alunos):
    with open(ARQUIVO_JSON, 'w', encoding='utf-8') as f:
        json.dump([a.to_dict() for a in alunos], f, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    alunos = carregar_alunos()
    turma_filtro = request.args.get('turma', '')
    if turma_filtro:
        alunos = [a for a in alunos if a.turma.lower() == turma_filtro.lower()]
    alunos.sort(key=lambda a: a.nome.lower())
    turmas = sorted({a.turma for a in carregar_alunos()})
    return render_template('index.html', alunos=alunos, turmas=turmas, filtro=turma_filtro)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    turma = request.form['turma']
    disc = request.form['disc']
    obj = request.form['obj']
    trabalhos = request.form.getlist('trabalhos')
    trabalhos = [t for t in trabalhos if t.strip()]
    aluno = Aluno(nome, turma, disc, obj, trabalhos)
    alunos = carregar_alunos()
    alunos.append(aluno)
    salvar_alunos(alunos)
    flash(f'Aluno {nome} adicionado!', 'success')
    return redirect(url_for('index'))

@app.route('/remover/<nome>')
def remover(nome):
    alunos = carregar_alunos()
    alunos = [a for a in alunos if a.nome.lower() != nome.lower()]
    salvar_alunos(alunos)
    flash(f'Aluno {nome} removido!', 'info')
    return redirect(url_for('index'))

@app.route('/atualizar/<nome>', methods=['POST'])
def atualizar(nome):
    nova_turma = request.form.get('turma')
    nova_disc = request.form.get('disc')
    nova_obj = request.form.get('obj')
    novos_trabalhos = request.form.getlist('trabalhos')
    novos_trabalhos = [t for t in novos_trabalhos if t.strip()]

    alunos = carregar_alunos()
    for aluno in alunos:
        if aluno.nome.lower() == nome.lower():
            if nova_turma:
                aluno.turma = nova_turma.strip()
            if nova_disc:
                aluno.nota_discursiva = float(nova_disc)
            if nova_obj:
                aluno.nota_objetiva = float(nova_obj)
            if novos_trabalhos:
                aluno.trabalhos = [float(t) for t in novos_trabalhos]
            aluno.soma = aluno.nota_discursiva + aluno.nota_objetiva + sum(aluno.trabalhos)
            break
    salvar_alunos(alunos)
    flash(f'Dados de {nome} atualizados!', 'success')
    return redirect(url_for('index'))

@app.route('/atualizar_nota', methods=['POST'])
def atualizar_nota():
    nome = request.form['nome']
    tipo = request.form['tipo']
    valor = request.form['valor']
    try:
        valor = float(valor)
        if not (0 <= valor <= 10):
            return jsonify({'status': 'error', 'message': 'Nota deve ser entre 0 e 10'}), 400
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Valor inválido'}), 400

    alunos = carregar_alunos()
    for aluno in alunos:
        if aluno.nome.lower() == nome.lower():
            if tipo == 'discursiva':
                aluno.nota_discursiva = valor
            elif tipo == 'objetiva':
                aluno.nota_objetiva = valor
            aluno.soma = aluno.nota_discursiva + aluno.nota_objetiva + sum(aluno.trabalhos)
            salvar_alunos(alunos)
            return jsonify({'status': 'success', 'nova_soma': aluno.soma})
    return jsonify({'status': 'error', 'message': 'Aluno não encontrado'}), 404

@app.route('/atualizar_campo', methods=['POST'])
def atualizar_campo():
    nome_aluno = request.form['nome']
    campo = request.form['campo']
    alunos = carregar_alunos()
    aluno = next((a for a in alunos if a.nome.lower() == nome_aluno.lower()), None)
    if not aluno:
        return jsonify({'status': 'error', 'message': 'Aluno não encontrado'}), 404

    try:
        if campo == 'nome':
            novo_nome = request.form['valor'].strip()
            if not novo_nome:
                return jsonify({'status': 'error', 'message': 'Nome não pode ser vazio'}), 400
            aluno.nome = novo_nome
        elif campo == 'turma':
            nova_turma = request.form['valor'].strip()
            if not nova_turma:
                return jsonify({'status': 'error', 'message': 'Turma não pode ser vazia'}), 400
            aluno.turma = nova_turma
        elif campo == 'nota_discursiva' or campo == 'nota_objetiva':
            valor = float(request.form['valor'])
            if not (0 <= valor <= 10):
                return jsonify({'status': 'error', 'message': 'Nota deve ser entre 0 e 10'}), 400
            if campo == 'nota_discursiva':
                aluno.nota_discursiva = valor
            else:
                aluno.nota_objetiva = valor
        elif campo == 'trabalho_adicionar':
            valor = float(request.form['valor'])
            if not (0 <= valor <= 10):
                return jsonify({'status': 'error', 'message': 'Nota deve ser entre 0 e 10'}), 400
            aluno.trabalhos.append(valor)
        elif campo == 'trabalho_remover':
            indice = int(request.form['indice'])
            if 0 <= indice < len(aluno.trabalhos):
                aluno.trabalhos.pop(indice)
            else:
                return jsonify({'status': 'error', 'message': 'Índice inválido'}), 400
        elif campo == 'trabalho_editar':
            indice = int(request.form['indice'])
            valor = float(request.form['valor'])
            if not (0 <= valor <= 10):
                return jsonify({'status': 'error', 'message': 'Nota deve ser entre 0 e 10'}), 400
            if 0 <= indice < len(aluno.trabalhos):
                aluno.trabalhos[indice] = valor
            else:
                return jsonify({'status': 'error', 'message': 'Índice inválido'}), 400
        else:
            return jsonify({'status': 'error', 'message': 'Campo desconhecido'}), 400

        aluno.soma = aluno.nota_discursiva + aluno.nota_objetiva + sum(aluno.trabalhos)
        salvar_alunos(alunos)
        return jsonify({'status': 'success', 'nova_soma': aluno.soma})
    except (ValueError, KeyError) as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)