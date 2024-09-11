import sqlite3
import pickle

class No:
    def __init__(self, pergunta=None, animal=None):
        self.pergunta = pergunta
        self.animal = animal
        self.sim = None
        self.nao = None

class ArvoreDecisaoDAO:
    def __init__(self, arquivo_pickle='arvore_decisao.pkl', db_name='animais.db'):
        self.arquivo_pickle = arquivo_pickle
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.create_table()

    def create_table(self):
        with self.conn as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS animais (
                    nome TEXT PRIMARY KEY,
                    frequencia INTEGER
                )
            ''')

    def atualizar_frequencia(self, animal):
        with self.conn as conn:
            conn.execute('''
                INSERT INTO animais (nome, frequencia)
                VALUES (?, 1)
                ON CONFLICT(nome) DO UPDATE SET frequencia = frequencia + 1
            ''', (animal,))

    def salvar_arvore(self, raiz):
        with open(self.arquivo_pickle, 'wb') as f:
            pickle.dump(raiz, f)

    def carregar_arvore(self):
        try:
            with open(self.arquivo_pickle, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            return None

    def obter_animais(self):
        with self.conn as conn:
            cursor = conn.execute('SELECT nome, frequencia FROM animais')
            return cursor.fetchall()

class JogoAdivinhacaoAnimal:
    def __init__(self):
        self.dao = ArvoreDecisaoDAO()
        self.raiz = self.dao.carregar_arvore()
        if not self.raiz:
            self.inicializar_arvore()

    def inicializar_arvore(self):
        self.raiz = No(pergunta="O animal vive na água?")
        self.raiz.sim = No(pergunta="O animal é um mamífero?")
        self.raiz.sim.sim = No(animal="Baleia")
        self.raiz.sim.nao = No(animal="Peixe")
        self.raiz.nao = No(pergunta="O animal pode voar?")
        self.raiz.nao.sim = No(animal="Pássaro")
        self.raiz.nao.nao = No(pergunta="O animal tem quatro patas?")
        self.raiz.nao.nao.sim = No(animal="Cachorro")
        self.raiz.nao.nao.nao = No(animal="Cobra")

    def obter_resposta(self, mensagem):
        resposta = input(mensagem).strip().lower()
        while resposta not in ["sim", "não", "nao"]:
            resposta = input("Resposta inválida. Por favor, responda com 'sim' ou 'não': ").strip().lower()
        return resposta

    def fazer_pergunta(self, no):
        if no.animal:
            resposta = self.obter_resposta(f"Você está pensando em um {no.animal}? (sim/não): ")
            if resposta in ["sim"]:
                print("Acertei!")
                self.dao.atualizar_frequencia(no.animal)
            else:
                self.aprender(no)
        else:
            resposta = self.obter_resposta(f"{no.pergunta} (sim/não): ")
            if resposta in ["sim"]:
                self.fazer_pergunta(no.sim)
            else:
                self.fazer_pergunta(no.nao)

    def aprender(self, no):
        animal = input("Qual animal você estava pensando? ").strip()
        pergunta = input(f"Faça uma pergunta que diferencie um {animal} de um {no.animal}: ").strip()
        resposta = self.obter_resposta(f"Para um {animal}, qual seria a resposta para essa pergunta? (sim/não): ")

        novo_no_animal = No(animal=animal)
        novo_no_pergunta = No(pergunta=pergunta)

        if resposta == "sim":
            novo_no_pergunta.sim = novo_no_animal
            novo_no_pergunta.nao = No(animal=no.animal)
        else:
            novo_no_pergunta.nao = novo_no_animal
            novo_no_pergunta.sim = No(animal=no.animal)

        no.pergunta = novo_no_pergunta.pergunta
        no.animal = None
        no.sim = novo_no_pergunta.sim
        no.nao = novo_no_pergunta.nao

        self.dao.salvar_arvore(self.raiz)

    def bubble_sort(self, animais):
        n = len(animais)
        for i in range(n):
            for j in range(0, n-i-1):
                if animais[j][1] < animais[j+1][1]:  # Ordena por frequência (descendente)
                    animais[j], animais[j+1] = animais[j+1], animais[j]
        return animais

    def exibir_animais_ordenados(self):
        animais = self.dao.obter_animais()
        if animais:
            animais_ordenados = self.bubble_sort(animais)
            print("\nAnimais conhecidos (ordenados por frequência de acertos):")
            for animal, frequencia in animais_ordenados:
                print(f"{animal}: {frequencia} acertos")
        else:
            print("Nenhum animal registrado ainda.")

    def jogar(self):
        print("Pense em um animal e eu tentarei adivinhar.")
        self.fazer_pergunta(self.raiz)
        self.exibir_animais_ordenados()

if __name__ == "__main__":
    jogo = JogoAdivinhacaoAnimal()
    while True:
        jogo.jogar()
        if input("Quer jogar novamente? (sim/não): ").strip().lower() != "sim":
            break
