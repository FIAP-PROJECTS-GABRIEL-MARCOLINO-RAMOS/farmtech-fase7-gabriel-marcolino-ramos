import sqlite3

# Conexão e criação da tabela
conn = sqlite3.connect('sensores.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS leituras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fosforo INTEGER,
    potassio INTEGER,
    ph INTEGER,
    umidade REAL,
    irrigacao INTEGER
)
''')
conn.commit()

def inserir_leitura(fosforo, potassio, ph, umidade, irrigacao):
    c.execute('INSERT INTO leituras (fosforo, potassio, ph, umidade, irrigacao) VALUES (?, ?, ?, ?, ?)',
              (fosforo, potassio, ph, umidade, irrigacao))
    conn.commit()

def consultar_leituras():
    c.execute('SELECT * FROM leituras')
    return c.fetchall()

def atualizar_leitura(id, fosforo, potassio, ph, umidade, irrigacao):
    c.execute('''UPDATE leituras SET fosforo=?, potassio=?, ph=?, umidade=?, irrigacao=? WHERE id=?''',
              (fosforo, potassio, ph, umidade, irrigacao, id))
    conn.commit()

def remover_leitura(id):
    c.execute('DELETE FROM leituras WHERE id=?', (id,))
    conn.commit()

# Exemplo de uso
if __name__ == "__main__":
    inserir_leitura(1, 1, 1200, 55.0, 1)
    print(consultar_leituras())
    atualizar_leitura(1, 0, 1, 1100, 65.0, 0)
    print(consultar_leituras())
    remover_leitura(1)
    print(consultar_leituras()) 
    inserir_leitura(1, 1, 1200, 55.0, 1)
    inserir_leitura(0, 1, 1100, 65.0, 0)
    inserir_leitura(1, 0, 1300, 45.0, 1)