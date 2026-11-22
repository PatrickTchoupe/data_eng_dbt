"""Simule un outil d'ingestion : charge les données TPC-H dans le schéma RAW.
Usage : python scripts/load_raw.py 1992-01-01 1996-01-01
"""
import sys
import duckdb

SOURCE_DB = "tpch_source.duckdb"   # le "système source" (l'ERP du grossiste)
TARGET_DB = "data_eng_dbt.duckdb"  # ton entrepôt, celui que dbt transforme

# 1. Générer le système source une seule fois
src = duckdb.connect(SOURCE_DB)
src.execute("INSTALL tpch; LOAD tpch;")
existing = [r[0] for r in src.execute(
    "select table_name from information_schema.tables").fetchall()]
if "orders" not in existing:
    print("Génération des données TPC-H (une seule fois)...")
    src.execute("CALL dbgen(sf = 1)")
src.close()

# 2. Charger un lot dans RAW
start, end = sys.argv[1], sys.argv[2]
con = duckdb.connect(TARGET_DB)
con.execute(f"ATTACH '{SOURCE_DB}' AS src (READ_ONLY)")
con.execute("CREATE SCHEMA IF NOT EXISTS raw")

# Tables de référence : copiées en entier si absentes
for t in ["region", "nation", "customer", "part", "supplier"]:
    con.execute(f"""CREATE TABLE IF NOT EXISTS raw.{t} AS
                    SELECT *, now() AS _loaded_at FROM src.main.{t}""")

# Tables de faits : on crée la structure vide, puis on insère le lot
con.execute("""CREATE TABLE IF NOT EXISTS raw.orders AS
               SELECT *, now() AS _loaded_at FROM src.main.orders LIMIT 0""")
con.execute("""CREATE TABLE IF NOT EXISTS raw.lineitem AS
               SELECT *, now() AS _loaded_at FROM src.main.lineitem LIMIT 0""")

con.execute("""INSERT INTO raw.orders
               SELECT *, now() FROM src.main.orders
               WHERE o_orderdate >= ? AND o_orderdate < ?""", [start, end])
con.execute("""INSERT INTO raw.lineitem
               SELECT l.*, now() FROM src.main.lineitem l
               JOIN src.main.orders o ON l.l_orderkey = o.o_orderkey
               WHERE o.o_orderdate >= ? AND o.o_orderdate < ?""", [start, end])

n = con.execute("SELECT count(*) FROM raw.orders").fetchone()[0]
print(f"Lot {start} -> {end} chargé. raw.orders contient maintenant {n} lignes.")
con.close()