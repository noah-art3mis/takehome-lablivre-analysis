-- Schema para banco de dados de Projetos de Investimento em Infraestrutura
-- Distrito Federal - Brasil
-- Fonte: API ObrasGov

-- =============================================================================
-- TABELAS DE ENTIDADES
-- =============================================================================

-- Tabela de instituições (tomadores, executores e repassadores)
CREATE TABLE IF NOT EXISTS instituicoes (
    codigo TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    sigla TEXT,
    tipo TEXT
);

CREATE INDEX IF NOT EXISTS idx_instituicoes_nome ON instituicoes(nome);

-- Tabela de eixos (dimensões estratégicas dos projetos)
CREATE TABLE IF NOT EXISTS eixos (
    id TEXT PRIMARY KEY,
    descricao TEXT NOT NULL
);

-- Tabela de tipos (categorias de projetos vinculadas a eixos)
CREATE TABLE IF NOT EXISTS tipos (
    id TEXT PRIMARY KEY,
    descricao TEXT NOT NULL,
    idEixo TEXT,
    FOREIGN KEY (idEixo) REFERENCES eixos(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_tipos_eixo ON tipos(idEixo);

-- Tabela de subtipos (subcategorias vinculadas a tipos)
CREATE TABLE IF NOT EXISTS subtipos (
    id TEXT PRIMARY KEY,
    descricao TEXT NOT NULL,
    idTipo TEXT,
    FOREIGN KEY (idTipo) REFERENCES tipos(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_subtipos_tipo ON subtipos(idTipo);

-- =============================================================================
-- TABELA PRINCIPAL: PROJETOS DE INVESTIMENTO
-- =============================================================================

CREATE TABLE IF NOT EXISTS projeto_investimento (
    idUnico TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT NOT NULL,
    funcaoSocial TEXT NOT NULL,
    metaGlobal TEXT NOT NULL,
    
    -- Localização
    cep TEXT,
    endereco TEXT,
    uf TEXT NOT NULL DEFAULT 'DF',
    
    -- Datas previstas
    dataInicialPrevista DATE,
    dataFinalPrevista DATE,
    
    -- Datas efetivas
    dataInicialEfetiva DATE,
    dataFinalEfetiva DATE,
    
    -- Datas administrativas
    dataCadastro DATE NOT NULL,
    dataSituacao DATE NOT NULL,
    
    -- Categorias
    natureza TEXT NOT NULL CHECK(natureza IN ('Obra', 'Projeto', 'Projeto de Investimento em Infraestrutura', 'Estudo', 'Outros')),
    naturezaOutras TEXT,
    especie TEXT CHECK(especie IN ('Construção', 'Ampliação', 'Reforma', 'Recuperação', 'Fabricação', 'Máquinas e Equipamentos')),
    situacao TEXT NOT NULL CHECK(situacao IN ('Cadastrada', 'Em execução', 'Concluída', 'Paralisada', 'Cancelada', 'Inacabada', 'Inativada')),
    
    -- Informações adicionais
    descPlanoNacionalPoliticaVinculado TEXT,
    observacoesPertinentes TEXT,
    
    -- Métricas de impacto
    qdtEmpregosGerados REAL,
    descPopulacaoBeneficiada TEXT,
    populacaoBeneficiada REAL,
    
    -- Tecnologia
    isModeladaPorBim BOOLEAN
);

-- Índices para queries comuns
CREATE INDEX IF NOT EXISTS idx_projeto_natureza ON projeto_investimento(natureza);
CREATE INDEX IF NOT EXISTS idx_projeto_situacao ON projeto_investimento(situacao);
CREATE INDEX IF NOT EXISTS idx_projeto_especie ON projeto_investimento(especie);
CREATE INDEX IF NOT EXISTS idx_projeto_data_cadastro ON projeto_investimento(dataCadastro);
CREATE INDEX IF NOT EXISTS idx_projeto_data_inicial_prevista ON projeto_investimento(dataInicialPrevista);
CREATE INDEX IF NOT EXISTS idx_projeto_bim ON projeto_investimento(isModeladaPorBim);

-- =============================================================================
-- TABELAS DE RELACIONAMENTO (MANY-TO-MANY)
-- =============================================================================

-- Relacionamento: Projeto <-> Instituições Tomadoras
CREATE TABLE IF NOT EXISTS projeto_tomadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idUnico TEXT NOT NULL,
    codigo TEXT NOT NULL,
    nome TEXT NOT NULL,
    FOREIGN KEY (idUnico) REFERENCES projeto_investimento(idUnico) ON DELETE CASCADE,
    FOREIGN KEY (codigo) REFERENCES instituicoes(codigo) ON DELETE CASCADE,
    UNIQUE(idUnico, codigo)
);

CREATE INDEX IF NOT EXISTS idx_projeto_tomadores_projeto ON projeto_tomadores(idUnico);
CREATE INDEX IF NOT EXISTS idx_projeto_tomadores_instituicao ON projeto_tomadores(codigo);

-- Relacionamento: Projeto <-> Instituições Executoras
CREATE TABLE IF NOT EXISTS projeto_executores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idUnico TEXT NOT NULL,
    codigo TEXT NOT NULL,
    nome TEXT NOT NULL,
    FOREIGN KEY (idUnico) REFERENCES projeto_investimento(idUnico) ON DELETE CASCADE,
    FOREIGN KEY (codigo) REFERENCES instituicoes(codigo) ON DELETE CASCADE,
    UNIQUE(idUnico, codigo)
);

CREATE INDEX IF NOT EXISTS idx_projeto_executores_projeto ON projeto_executores(idUnico);
CREATE INDEX IF NOT EXISTS idx_projeto_executores_instituicao ON projeto_executores(codigo);

-- Relacionamento: Projeto <-> Instituições Repassadoras
CREATE TABLE IF NOT EXISTS projeto_repassadores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idUnico TEXT NOT NULL,
    codigo TEXT NOT NULL,
    nome TEXT NOT NULL,
    FOREIGN KEY (idUnico) REFERENCES projeto_investimento(idUnico) ON DELETE CASCADE,
    FOREIGN KEY (codigo) REFERENCES instituicoes(codigo) ON DELETE CASCADE,
    UNIQUE(idUnico, codigo)
);

CREATE INDEX IF NOT EXISTS idx_projeto_repassadores_projeto ON projeto_repassadores(idUnico);
CREATE INDEX IF NOT EXISTS idx_projeto_repassadores_instituicao ON projeto_repassadores(codigo);

-- Relacionamento: Projeto <-> Eixos
CREATE TABLE IF NOT EXISTS projeto_eixos (
    projeto_id INTEGER PRIMARY KEY AUTOINCREMENT,
    idUnico TEXT NOT NULL,
    id TEXT NOT NULL,
    descricao TEXT NOT NULL,
    FOREIGN KEY (idUnico) REFERENCES projeto_investimento(idUnico) ON DELETE CASCADE,
    FOREIGN KEY (id) REFERENCES eixos(id) ON DELETE CASCADE,
    UNIQUE(idUnico, id)
);

CREATE INDEX IF NOT EXISTS idx_projeto_eixos_projeto ON projeto_eixos(idUnico);
CREATE INDEX IF NOT EXISTS idx_projeto_eixos_eixo ON projeto_eixos(id);

-- Relacionamento: Projeto <-> Tipos
CREATE TABLE IF NOT EXISTS projeto_tipos (
    projeto_id INTEGER PRIMARY KEY AUTOINCREMENT,
    idUnico TEXT NOT NULL,
    id TEXT NOT NULL,
    descricao TEXT NOT NULL,
    idEixo TEXT,
    FOREIGN KEY (idUnico) REFERENCES projeto_investimento(idUnico) ON DELETE CASCADE,
    FOREIGN KEY (id) REFERENCES tipos(id) ON DELETE CASCADE,
    UNIQUE(idUnico, id)
);

CREATE INDEX IF NOT EXISTS idx_projeto_tipos_projeto ON projeto_tipos(idUnico);
CREATE INDEX IF NOT EXISTS idx_projeto_tipos_tipo ON projeto_tipos(id);

-- Relacionamento: Projeto <-> Subtipos
CREATE TABLE IF NOT EXISTS projeto_subtipos (
    projeto_id INTEGER PRIMARY KEY AUTOINCREMENT,
    idUnico TEXT NOT NULL,
    id TEXT NOT NULL,
    descricao TEXT NOT NULL,
    idTipo TEXT,
    FOREIGN KEY (idUnico) REFERENCES projeto_investimento(idUnico) ON DELETE CASCADE,
    FOREIGN KEY (id) REFERENCES subtipos(id) ON DELETE CASCADE,
    UNIQUE(idUnico, id)
);

CREATE INDEX IF NOT EXISTS idx_projeto_subtipos_projeto ON projeto_subtipos(idUnico);
CREATE INDEX IF NOT EXISTS idx_projeto_subtipos_subtipo ON projeto_subtipos(id);

-- =============================================================================
-- TABELA DE FONTES DE RECURSO (ONE-TO-MANY)
-- =============================================================================

CREATE TABLE IF NOT EXISTS fontes_de_recurso (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idUnico TEXT NOT NULL,
    origem TEXT NOT NULL CHECK(origem IN ('Federal', 'Estadual', 'Municipal', 'Privado', 'Internacional')),
    valorInvestimentoPrevisto REAL CHECK(valorInvestimentoPrevisto >= 0),
    FOREIGN KEY (idUnico) REFERENCES projeto_investimento(idUnico) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fontes_recurso_projeto ON fontes_de_recurso(idUnico);
CREATE INDEX IF NOT EXISTS idx_fontes_recurso_origem ON fontes_de_recurso(origem);

-- =============================================================================
-- VIEWS ÚTEIS
-- =============================================================================

-- View: Projetos com valor total de investimento
CREATE VIEW IF NOT EXISTS v_projetos_investimento_total AS
SELECT 
    p.idUnico,
    p.nome,
    p.natureza,
    p.situacao,
    p.dataInicialPrevista,
    p.dataFinalPrevista,
    COALESCE(SUM(f.valorInvestimentoPrevisto), 0) AS valorTotalPrevisto,
    COUNT(DISTINCT f.origem) AS qtdFontesRecurso
FROM projeto_investimento p
LEFT JOIN fontes_de_recurso f ON p.idUnico = f.idUnico
GROUP BY p.idUnico;

-- View: Projetos com suas instituições
CREATE VIEW IF NOT EXISTS v_projetos_instituicoes AS
SELECT 
    p.idUnico,
    p.nome,
    p.natureza,
    p.situacao,
    GROUP_CONCAT(DISTINCT pt.nome) AS tomadores,
    GROUP_CONCAT(DISTINCT pe.nome) AS executores,
    GROUP_CONCAT(DISTINCT pr.nome) AS repassadores
FROM projeto_investimento p
LEFT JOIN projeto_tomadores pt ON p.idUnico = pt.idUnico
LEFT JOIN projeto_executores pe ON p.idUnico = pe.idUnico
LEFT JOIN projeto_repassadores pr ON p.idUnico = pr.idUnico
GROUP BY p.idUnico;

-- View: Estatísticas por natureza de projeto
CREATE VIEW IF NOT EXISTS v_estatisticas_natureza AS
SELECT 
    natureza,
    COUNT(*) AS quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM projeto_investimento), 2) AS percentual,
    SUM(CASE WHEN isModeladaPorBim = 1 THEN 1 ELSE 0 END) AS projetos_bim,
    AVG(populacaoBeneficiada) AS media_populacao_beneficiada,
    SUM(qdtEmpregosGerados) AS total_empregos_gerados
FROM projeto_investimento
GROUP BY natureza
ORDER BY quantidade DESC;

-- View: Projetos atrasados (data final prevista passou e não está concluído)
CREATE VIEW IF NOT EXISTS v_projetos_atrasados AS
SELECT 
    idUnico,
    nome,
    natureza,
    situacao,
    dataFinalPrevista,
    JULIANDAY('now') - JULIANDAY(dataFinalPrevista) AS dias_atraso
FROM projeto_investimento
WHERE dataFinalPrevista < DATE('now')
    AND situacao NOT IN ('Concluída', 'Cancelada', 'Inativada')
ORDER BY dias_atraso DESC;

-- =============================================================================
-- COMENTÁRIOS SOBRE O SCHEMA
-- =============================================================================

/*
DECISÕES DE DESIGN:

1. TIPOS DE DADOS:
   - TEXT para IDs porque o sistema original usa strings (ex: "50379.53-54")
   - REAL para valores numéricos (permite NULL para ausência de dados)
   - DATE para datas (SQLite armazena como TEXT mas valida formato)
   - BOOLEAN para flags (SQLite armazena como INTEGER 0/1)

2. CONSTRAINTS:
   - CHECK constraints para valores categóricos conhecidos
   - NOT NULL onde os dados mostram sempre presentes
   - UNIQUE constraints para evitar duplicatas em relacionamentos
   - Foreign keys com ON DELETE CASCADE/SET NULL apropriados

3. ÍNDICES:
   - Criados em colunas frequentemente usadas em WHERE, JOIN e GROUP BY
   - Índices compostos para relacionamentos many-to-many

4. NORMALIZAÇÃO:
   - Instituições unificadas (tomadores/executores/repassadores compartilham códigos)
   - Eixos -> Tipos -> Subtipos em hierarquia
   - Fontes de recurso separadas (one-to-many) para permitir múltiplas fontes

5. VIEWS:
   - Facilitam queries comuns
   - Pré-calculam agregações úteis
   - Desnormalizam dados para relatórios

PRÓXIMOS PASSOS:
- Adicionar triggers para validação de dados
- Criar procedures para cálculos complexos (ex: duração efetiva vs prevista)
- Adicionar tabela de auditoria para rastrear mudanças
- Implementar particionamento se volume crescer significativamente
*/

