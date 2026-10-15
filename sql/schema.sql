PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS produtor (
 id INTEGER PRIMARY KEY, nome TEXT NOT NULL, propriedade TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cultura (
 id INTEGER PRIMARY KEY, nome TEXT NOT NULL UNIQUE, produtor_id INTEGER NOT NULL REFERENCES produtor(id)
);
CREATE TABLE IF NOT EXISTS talhao (
 id INTEGER PRIMARY KEY, nome TEXT NOT NULL UNIQUE, cultura_id INTEGER NOT NULL REFERENCES cultura(id),
 area_m2 REAL NOT NULL CHECK(area_m2 > 0), dose_l_ha REAL NOT NULL CHECK(dose_l_ha >= 0),
 ativo INTEGER NOT NULL DEFAULT 1 CHECK(ativo IN (0,1)), criado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sensor (
 id TEXT PRIMARY KEY, talhao_id INTEGER NOT NULL REFERENCES talhao(id), tipo TEXT NOT NULL,
 origem TEXT NOT NULL CHECK(origem IN ('simulado','manual','ESP32'))
);
CREATE TABLE IF NOT EXISTS leitura (
 id INTEGER PRIMARY KEY, sensor_id TEXT NOT NULL REFERENCES sensor(id), evento_id TEXT NOT NULL,
 observado_em TEXT NOT NULL, recebido_em TEXT NOT NULL,
 umidade_solo REAL CHECK(umidade_solo BETWEEN 0 AND 100),
 umidade_ar REAL CHECK(umidade_ar BETWEEN 0 AND 100),
 temperatura REAL CHECK(temperatura BETWEEN -40 AND 85),
 ph REAL CHECK(ph BETWEEN 0 AND 14), ph_simulado INTEGER NOT NULL CHECK(ph_simulado IN (0,1)),
 fosforo INTEGER NOT NULL CHECK(fosforo IN (0,1)), potassio INTEGER NOT NULL CHECK(potassio IN (0,1)),
 origem TEXT NOT NULL CHECK(origem IN ('simulado','manual','ESP32')),
 UNIQUE(sensor_id,evento_id)
);
CREATE TABLE IF NOT EXISTS operacao (
 id INTEGER PRIMARY KEY, talhao_id INTEGER NOT NULL REFERENCES talhao(id), criado_em TEXT NOT NULL,
 tipo TEXT NOT NULL, volume_l REAL NOT NULL CHECK(volume_l >= 0), observacao TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS visao (
 id INTEGER PRIMARY KEY, criado_em TEXT NOT NULL, arquivo TEXT NOT NULL, sha256 TEXT NOT NULL,
 modelo TEXT NOT NULL, resultado_json TEXT NOT NULL, tempo_ms REAL NOT NULL CHECK(tempo_ms>=0)
);
CREATE TABLE IF NOT EXISTS alerta (
 id INTEGER PRIMARY KEY, leitura_id INTEGER REFERENCES leitura(id), visao_id INTEGER REFERENCES visao(id),
 regra TEXT NOT NULL, chave TEXT NOT NULL UNIQUE, titulo TEXT NOT NULL, acao TEXT NOT NULL,
 criado_em TEXT NOT NULL, estado TEXT NOT NULL DEFAULT 'aberto' CHECK(estado IN ('aberto','resolvido')),
 CHECK((leitura_id IS NOT NULL) != (visao_id IS NOT NULL))
);
CREATE TABLE IF NOT EXISTS notificacao (
 id INTEGER PRIMARY KEY, alerta_id INTEGER NOT NULL UNIQUE REFERENCES alerta(id),
 estado TEXT NOT NULL DEFAULT 'pendente' CHECK(estado IN ('pendente','enviando','aceito_sns','falha','incerto')),
 tentativas INTEGER NOT NULL DEFAULT 0, message_id TEXT, erro TEXT, atualizado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_leitura_sensor_data ON leitura(sensor_id, observado_em);
CREATE INDEX IF NOT EXISTS idx_notificacao_estado ON notificacao(estado);
