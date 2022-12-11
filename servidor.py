from config import *
# Flask : necessario para criar rotas da api;
# Response : necessario para criar o retorno da api;
# request : necessario para interagir com o body enviado pelo cliente.
from flask import Flask, Response, request
# SQLAlchemy : necessaria para interagir com o banco de dados sem a necessidade
# de se trabalhar com manualmente com o ele.
from flask_sqlalchemy import SQLAlchemy
# Necessario para conexao com o banco de dados mysql.
import mysql.connector
# Necessario para se trabalhar com json.
import json

# Criando a aplicacao flask.
app = Flask(__name__)

# Configuracoes para acessar o banco de dados
# Obs: se a senha tiver algum caracter especial, deve ser inserido parametro
# charset.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{USER}:{PASS}@{DB_URL}/{DB}?charset=utf8mb4'

# Criando a classe SQLAlchemy e automatizando a conexao.
db = SQLAlchemy(app)

# Criando a tabela no banco de dados, onde e necessario extender o que esta
# definido em db, para trazer ferramentas predefinidas em Model.
class Usuarios(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(80))
    # Funcao para transformar um objeto em json.
    def para_json(self):
        return {'id': self.id, 'nome': self.nome, 'email': self.email}

# status : trata-se de status de retorno de protocolo http;
# nome_conteudo : trata-se de nome da chave;
# conteudo : trata-se do objeto retornado;
# mensagem=False : trata-se de eventual mensagem.
def retorna_resposta(status, nome_conteudo, conteudo, mensagem=False):
    # Criando um dicionario vazio.
    body = {}
    # Atribuindo um nome a uma chave um objeto em seguida.
    body[nome_conteudo] = conteudo
    # Na hipotese de haver mensagem, ela sera atribuida a uma chave.
    if mensagem:
        body['mensagem'] = mensagem
    # Response() : necessario para o retorno;
    # json.dumps() : necessario na conversao e retorno de json;
    # mimetype='application/json' : necessario para conversao em json.
    return Response(json.dumps(body), status=status, mimetype='application/json')

####################################################################################################

# Create : rota que permite inserir um novo usuario no banco de dados.
@app.route('/cadastra', methods=['POST'])
def insere():
    # Recebe um json atraves da interface.
    body = request.get_json()
    # Valida se as informacoes foram passadas por completo.
    try:
        # Recebe e atribui cada parametro ao valor correspondente no banco de
        # dados atraves da classe criada.
        usuario = Usuarios(nome=body['nome'], email=body['email'])
        # Invoca a funcao db, abre uma sessao e informa que deseja adicionar
        # os valores capturados na etapa anterior.
        db.session.add(usuario)
        # Funcao que comita a etapa anterior
        db.session.commit()
        # Retorna para a interface funcao de visualizacao de sucesso 
        return retorna_resposta(201, 'usuarios', usuario.para_json(), 'Usuario cadastrado com sucesso!')
    except Exception as e:
        print(e)
        return retorna_resposta(400, 'usuario', {}, 'Erro na tentativa de cadastro...')


####################################################################################################

# Read - one : rota para retornar apenas 1 usuario cadastrado em banco de
# dados, a partir de seu id.
@app.route('/consulta/<id>', methods=['GET'])
def consulta(id):
    # filter_by(id=id).first() : sera o responsavel por renderizar apenas o
    # usuario associado ao id digitado.
    usuario_objeto = Usuarios.query.filter_by(id=id).first()
    usuario_json = usuario_objeto.para_json()
    return retorna_resposta(200, 'usuario', usuario_json, 'Testando parametro mensagem... OK!')

# Read - all : rota para retornar todos os usuarios cadastrados no banco de
# dados.
@app.route('/consulta', methods=['GET'])
def consultas():
    # Atraves da classe construida e conectada com o banco de dados, efetua
    # uma busca e retorna todos os valores persistidos nele, armazenando em
    # em lista/variavel.
    usuarios_objetos = Usuarios.query.all()
    # Como a variavel acima retorna uma lista, e necessario percorre-la com
    # loop for, aplicando a funcao criada na classe para transformar cada
    # elemento em objeto e armazenar em variavel.
    usuarios_json = [usuario.para_json() for usuario in usuarios_objetos]
    # Para esse caso, e necessario aplicar a ferramenta json.dumps para
    # retornar a resposta da api.
    return retorna_resposta(200, 'usuarios', usuarios_json, 'Testando parametro mensagem... OK!')

####################################################################################################

# Update 1: rota para atualizar nome de usuario
@app.route('/atualiza-nome/<id>', methods=['PUT'])
def atualiza_nome(id):
    usuario_objeto = Usuarios.query.filter_by(id=id).first()
    body = request.get_json()
    try:
        if 'nome' in body:
            usuario_objeto.nome = body['nome']
            db.session.add(usuario_objeto)
            db.session.commit()
            return retorna_resposta(200, 'usuarios', usuario_objeto.para_json(), 'Nome atualizado com sucesso!')
    except Exception as e:
        print(e)
        return retorna_resposta(400, 'usuario', {}, 'Erro na tentativa de atualizar...')

# Update 2: rota para atualizar e-mail de usuario
@app.route('/atualiza-email/<id>', methods=['PUT'])
def atualiza_email(id):
    usuario_objeto = Usuarios.query.filter_by(id=id).first()
    body = request.get_json()
    try:
        if 'email' in body:
            usuario_objeto.email = body['email']
            db.session.add(usuario_objeto)
            db.session.commit()
            return retorna_resposta(200, 'usuarios', usuario_objeto.para_json(), 'E-mail atualizado com sucesso!')
    except Exception as e:
        print(e)
        return retorna_resposta(400, 'usuario', {}, 'Erro na tentativa de atualizar...')

####################################################################################################

# Delete : rota para deletar usuario
@app.route('/deleta/<id>', methods=['DELETE'])
def delete(id):
    usuario_objeto = Usuarios.query.filter_by(id=id).first()
    try:
        db.session.delete(usuario_objeto)
        db.session.commit()
        return retorna_resposta(200, 'usuarios', usuario_objeto.para_json(), 'Usuario deletado com sucesso!')
    except Exception as e:
        print(e)
        return retorna_resposta(400, 'usuario', {}, 'Erro na tentativa de deletar...')

####################################################################################################

# Condicional que verifica se a aplicacao flask criada e igual a principal e
# executa ela em caso positivo atraves de 'app.run()'. Os parametros indicam
# em qual computador sera executado, qual a porta e se a inicializacao sera
# automatica todas as vezes.
if __name__ == '__main__':
    app.run(host = 'localhost', port = 5000, debug = True)