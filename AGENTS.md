# database.py original (ERRADO)
db = Client(...)
clients   = db.use(DB_NAME, "clients")     # retorna self, _table = "clients"
merchants = db.use(DB_NAME, "merchants")   # retorna self, _table = "merchants" ← SOBRESCREVE
...
favorites = db.use(DB_NAME, "favorites")   # retorna self, _table = "favorites"
Todas as 16 variáveis apontam pro mesmo objeto. Quando chamava clients.exists(...), na verdade consultava a tabela favorites. Isso corrompeu o banco inteiro e gerou 500 em todas as rotas.  
Solução: criar Client separado por tabela via construtor: Client(..., database=DB, table="clients").
🧩 PortunusQL não aceita list/dict
Campos declarados como cart=[], favorites=[] no create() quebravam com:
TypeError: Unsupported value type for PortunusQL: list
Solução: json.dumps() ao gravar, json.loads() ao ler.
🔄 Corrupção em uma tabela quebra TODAS as operações
Um arquivo msgpack com duplicate field 'id' na tabela favorites fazia qualquer exists(), get() ou create() em qualquer tabela falhar. O erro apontava favorites mesmo operando em clients, dificultando o diagnóstico.
💾 drop_table() não remove arquivos do disco
Recriar tabelas deixava dados corrompidos em ~/.portunus/databases/.  
Solução: shutil.rmtree() + recriação completa.
🐚 Shell do agente trava com kill/pkill
Testes que usavam & + kill para gerenciar servidor uvicorn travavam o bash tool.