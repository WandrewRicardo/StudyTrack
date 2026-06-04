import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime


#definição janela principal
janela = tk.Tk()
janela.title("StudyTrack")
janela.geometry("1000x600")

#Conexão com Banco de Dados
conexao = sqlite3.connect("StudyTrack.db")
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
""")
conexao.commit()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS atividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    id_disciplina INTEGER NOT NULL,
    prazo TEXT,
    status TEXT,
    
    FOREIGN KEY (id_disciplina)
    REFERENCES disciplinas(id)
    )
""")
conexao.commit()

disciplina_alteracao = None
atividade_alteracao = None

#inserido as abas
abas = ttk.Notebook(janela)
aba_historico = ttk.Frame(abas)
aba_disciplinas = ttk.Frame(abas)
aba_atividades = ttk.Frame(abas)

abas.add(aba_atividades, text="Atividades")
abas.add(aba_disciplinas, text="Disciplinas")
abas.add(aba_historico, text="Histórico")
abas.pack(expand=True, fill="both")





#FUNCIONALIDADES ABA DISCIPLINAS

#carregando as disciplinas que já estão no DB
def load_disciplinas():
    cursor.execute("SELECT id, nome FROM disciplinas")
    disciplinas = cursor.fetchall()
    for disciplina in disciplinas:
        tabela_disciplinas.insert("", "end", values=(disciplina[0], disciplina[1]))

def load_atividades():
    cursor.execute("""
        SELECT atividades.id, atividades.titulo, disciplinas.nome, atividades.prazo, atividades.status FROM atividades
        INNER JOIN disciplinas ON atividades.id_disciplina = disciplinas.id
    """)
    atividades = cursor.fetchall()
    for atividade in atividades:
        tabela_atividades.insert("", "end", values = (atividade[0], atividade[1],atividade[2],
        atividade[3], atividade[4]))

def load_disciplinas_combobox():
    cursor.execute("SELECT nome FROM disciplinas")
    disciplinas = cursor.fetchall()
    lista_disciplinas = []
    for disciplina in disciplinas:
        lista_disciplinas.append(disciplina[0])
    combo_disciplina["values"] = lista_disciplinas

#CAPITURA DOS EVENTOS
def add_disciplina():
    global disciplina_alteracao
    nome = input_nomeDisciplina.get()
    if not nome:
        return
    if disciplina_alteracao:
        dados = tabela_disciplinas.item(disciplina_alteracao)
        id_disciplina = dados["values"][0]

        cursor.execute(
            """
            UPDATE disciplinas SET nome = ? WHERE id = ?
            """, (nome,id_disciplina)
        )
        conexao.commit()

        tabela_disciplinas.item(
            disciplina_alteracao,
            values=(id_disciplina, nome)
        )
        disciplina_alteracao = None
    else:
        cursor.execute("INSERT INTO disciplinas(nome) VALUES(?)",(nome,))
        conexao.commit()

        id_disciplina = cursor.lastrowid
        tabela_disciplinas.insert("","end",values=(id_disciplina, nome))

    input_nomeDisciplina.delete(0, "end")
    load_disciplinas_combobox()
    carregar_historico()

def delete_disciplina():
    selecionado = tabela_disciplinas.selection()
    if not selecionado:
        return
    dados = tabela_disciplinas.item(selecionado[0])
    id_disciplina = dados["values"][0]

    cursor.execute(
        "DELETE FROM disciplinas WHERE id = ?",(id_disciplina,)
    )
    conexao.commit()
    tabela_disciplinas.delete(selecionado[0])
    carregar_historico()

def editar_disciplina():
    global disciplina_alteracao
    selecionado = tabela_disciplinas.selection()
    if not selecionado:
        return
    disciplina_alteracao = selecionado[0]
    dados = tabela_disciplinas.item(disciplina_alteracao)

    nome = dados["values"][1]

    input_nomeDisciplina.delete(0, "end")
    input_nomeDisciplina.insert(0, nome)

def add_atividade():
    global atividade_alteracao
    titulo = input_titulo.get()
    disciplina = combo_disciplina.get()
    prazo = input_prazo.get()
    status = combo_status.get()
    if not titulo or not disciplina:
        return

    cursor.execute(
        "SELECT id FROM disciplinas WHERE nome = ?",(disciplina,)
    )

    resultado = cursor.fetchone()
    id_disciplina = resultado[0]
    if atividade_alteracao:
        dados = tabela_atividades.item(atividade_alteracao)
        id_atividade = dados["values"][0]
        cursor.execute(
            """
            UPDATE atividades SET titulo = ?, id_disciplina = ?, prazo = ?, status = ? WHERE id = ?
            """,(titulo, id_disciplina, prazo, status,id_atividade)
        )
        conexao.commit()

        tabela_atividades.item(
            atividade_alteracao,
            values=(id_atividade, titulo, disciplina, prazo, status)
        )
        atividade_alteracao = None

    else:

        cursor.execute(
            """
            INSERT INTO atividades (titulo, id_disciplina, prazo, status)
            VALUES (?, ?, ?, ?)
            """,(titulo, id_disciplina, prazo, status)
        )
        conexao.commit()
        id_atividade = cursor.lastrowid
        tabela_atividades.insert("","end", values=(id_atividade, titulo, disciplina, prazo, status)
        )

    input_titulo.delete(0, "end")
    input_prazo.delete(0, "end")
    combo_disciplina.set("")
    combo_status.current(0)
    carregar_historico()

def delete_atividade():
    selecionado = tabela_atividades.selection()
    if not selecionado:
        return
    dados = tabela_atividades.item(selecionado[0])
    id_atividade = dados["values"][0]

    cursor.execute(
        "DELETE FROM atividades WHERE id = ?", (id_atividade,)
    )
    conexao.commit()
    tabela_atividades.delete(selecionado[0])
    carregar_historico()

def editar_atividade():
    global atividade_alteracao
    selecionado = tabela_atividades.selection()
    if not selecionado:
        return
    atividade_alteracao = selecionado[0]
    dados = tabela_atividades.item(atividade_alteracao)

    input_titulo.delete(0, "end")
    input_titulo.insert(0, dados["values"][1])

    combo_disciplina.set(dados["values"][2])

    input_prazo.delete(0, "end")
    input_prazo.insert(0, dados["values"][3])

    combo_status.set(dados["values"][4])


def carregar_historico():
    cursor.execute("SELECT COUNT(*) FROM disciplinas")
    total_disciplinas = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM atividades")
    total_atividades = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM atividades WHERE status = 'Concluída'")
    concluidas = cursor.fetchone()[0]

    if total_atividades > 0:
        percentual = (concluidas / total_atividades) * 100
    else:
        percentual = 0

    cursor.execute("SELECT COUNT(*) FROM atividades WHERE status = 'Em Andamento'")
    andamentos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM atividades WHERE status = 'Pendente'")
    pendentes = cursor.fetchone()[0]

    lbl_total_disciplinas.config(
        text=f"Total de disciplinas: {total_disciplinas}",
    )
    lbl_total_atividades.config(
        text=f"Total de Atividades: {total_atividades}"
    )

    lbl_concluidas.config(
        text=f"Atividades Concluídas: {concluidas}"
    )

    lbl_pendentes.config(
        text=f"Atividades Pendentes: {pendentes}"
    )

    lbl_andamento.config(
        text=f"Atividades Em Andamento: {andamentos}"
    )
    lbl_percentual.config(
        text=f"Percentual Concluído: {percentual:.1f}%"
    )
    cursor.execute("""
        SELECT prazo FROM atividades WHERE status != 'Concluída'
        """)
    atividades = cursor.fetchall()
    atrasadas = 0
    hoje = datetime.now()
    for atividade in atividades:
        try:
            prazo = datetime.strptime(
                atividade[0],
                "%d/%m/%Y")
            if prazo < hoje:
                atrasadas += 1
        except:
            pass
    lbl_atrasadas.config(
        text=f"Atividades Atrasadas: {atrasadas}"
    )

#INTERFACE ABA DISCIPLINA
lbl_nomeDisciplina = ttk.Label(aba_disciplinas, text = "Nome da Disciplina")
lbl_nomeDisciplina.pack(pady = 10)
input_nomeDisciplina = ttk.Entry(aba_disciplinas, width= 40)
input_nomeDisciplina.pack(pady = 5)

btn_add = ttk.Button(aba_disciplinas, text = "Adicionar", command= add_disciplina)
btn_add.pack(pady = 10)

btn_excluir = ttk.Button(aba_disciplinas, text= "Excluir", command= delete_disciplina)
btn_excluir.pack(pady=5)

btn_editar = ttk.Button(aba_disciplinas, text = "Editar", command= editar_disciplina)
btn_editar.pack(pady=5)

tabela_disciplinas = ttk.Treeview(aba_disciplinas, columns = ("id", "disciplina",), show = "headings", height= 10)
tabela_disciplinas.heading("id", text = "ID")
tabela_disciplinas.heading("disciplina", text = " Nome da Disciplina")
tabela_disciplinas.pack(pady = 20, fill="x")
load_disciplinas()



#INTERFACE ABA ATIVIDADES
lbl_titulo = ttk.Label(aba_atividades, text = "Titulo Atividade")
lbl_titulo.pack(pady =10)
input_titulo = ttk.Entry(aba_atividades, width = 40)
input_titulo.pack(pady = 5)


lbl_disciplina = ttk.Label(aba_atividades, text = "Disciplina da atividade")
lbl_disciplina.pack(pady =10)
combo_disciplina = ttk.Combobox(aba_atividades, state="readonly", width= 37)
combo_disciplina.pack(pady=5)


lbl_prazo = ttk.Label(aba_atividades, text = "Prazo da atividade")
lbl_prazo.pack(pady =10)
input_prazo = ttk.Entry(aba_atividades, width = 40)
input_prazo.pack(pady = 5)


lbl_status = ttk.Label(aba_atividades, text = "Status atividade")
lbl_status.pack(pady =10)
combo_status = ttk.Combobox(aba_atividades, state="readonly",values= ["Pendente", "Em Andamento", "Concluída"], width= 37)
combo_status.pack(pady=5)
combo_status.current(0)

btn_add_atividades = ttk.Button(aba_atividades, text = "Adicionar", command= add_atividade)
btn_add_atividades.pack(pady = 5)
btn_excluir_atividades = ttk.Button(aba_atividades, text = "Excluir", command = delete_atividade)
btn_excluir_atividades.pack(pady = 5)
btn_editar_atividades = ttk.Button(aba_atividades, text = "Editar", command = editar_atividade)
btn_editar_atividades.pack(pady = 5)

tabela_atividades = ttk.Treeview(aba_atividades, columns = ("id", "titulo", "disciplina", "prazo", "status"), show= "headings", height= 10)
tabela_atividades.heading("id", text = "ID")
tabela_atividades.heading("titulo", text = "Título")
tabela_atividades.heading("disciplina", text = "Disciplina")
tabela_atividades.heading("prazo", text = "Prazo")
tabela_atividades.heading("status", text = "Status")
tabela_atividades.pack(pady = 20, fill="x")
load_atividades()
load_disciplinas_combobox()


#INTERFACE ABA HISTÓRICO
lbl_total_disciplinas = ttk.Label(aba_historico, text="Total de Disciplinas: 0", font=("Arial", 14))
lbl_total_disciplinas.pack(pady=10)

lbl_total_atividades = ttk.Label(aba_historico, text="Total de Atividades: 0", font=("Arial", 14))
lbl_total_atividades.pack(pady=10)

lbl_concluidas = ttk.Label(aba_historico, text="Atividades Concluídas: 0", font=("Arial", 14))
lbl_concluidas.pack(pady=10)

lbl_pendentes = ttk.Label(aba_historico, text="Atividades Pendentes: 0", font=("Arial", 14))
lbl_pendentes.pack(pady=10)

lbl_andamento = ttk.Label(aba_historico, text="Atividades Em Andamento: 0", font=("Arial", 14))
lbl_andamento.pack(pady=10)

lbl_percentual = ttk.Label(aba_historico, text="Percentual Concluído: 0%", font=("Arial", 14))
lbl_percentual.pack(pady=10)

lbl_atrasadas = ttk.Label(aba_historico, text="Atividades Atrasadas: 0", font=("Arial", 14))
lbl_atrasadas.pack(pady=10)

carregar_historico()


janela.mainloop()