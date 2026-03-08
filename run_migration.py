"""Run waitlist migration against Supabase."""
import asyncio
import asyncpg


async def main():
    conn = await asyncpg.connect(
        host="aws-1-eu-west-1.pooler.supabase.com",
        port=5432,
        user="postgres.rnadgazmouyqighkovsi",
        password="arv9uy!@mUWv2*K",
        database="postgres",
    )

    sql = """
    CREATE TABLE IF NOT EXISTS waitlist (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        role VARCHAR(50) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    """

    try:
        await conn.execute(sql)
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_waitlist_email ON waitlist(email);")
        await conn.execute("CREATE INDEX IF NOT EXISTS idx_waitlist_role ON waitlist(role);")
        print("Migration applied successfully!")

        result = await conn.fetchval("SELECT COUNT(*) FROM waitlist")
        print(f"Waitlist table exists, rows: {result}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
