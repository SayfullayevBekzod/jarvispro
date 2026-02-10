"""Eski cache ni tozalash"""
import sqlite3
import os

db_path = os.path.join("jarvis", "data", "jarvis.db")
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Sistema buyruqlari keshini tozalash
c.execute("DELETE FROM qa WHERE answer LIKE '%ishlamayapti%'")
c.execute("DELETE FROM qa WHERE answer LIKE '%xatolik%'")
c.execute("DELETE FROM qa WHERE question LIKE '%ovoz%'")
c.execute("DELETE FROM qa WHERE question LIKE '%batareya%'")
c.execute("DELETE FROM qa WHERE question LIKE '%soat%'")
c.execute("DELETE FROM qa WHERE question LIKE '%kompyuter%'")
c.execute("DELETE FROM qa WHERE question LIKE '%skrinshot%'")
c.execute("DELETE FROM qa WHERE question LIKE '%screenshot%'")

conn.commit()

# Qolgan yozuvlar
c.execute("SELECT COUNT(*) FROM qa")
count = c.fetchone()[0]
print(f"Cache tozalandi. Qolgan yozuvlar: {count}")

conn.close()
