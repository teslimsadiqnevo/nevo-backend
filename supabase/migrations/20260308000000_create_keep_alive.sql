-- Keep-alive table to prevent Supabase from pausing the project
CREATE TABLE IF NOT EXISTS keep_alive (
    id SERIAL PRIMARY KEY,
    pinged_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Only keep the latest 10 pings to avoid bloat
CREATE OR REPLACE FUNCTION trim_keep_alive() RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM keep_alive WHERE id NOT IN (
        SELECT id FROM keep_alive ORDER BY pinged_at DESC LIMIT 10
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER keep_alive_trim AFTER INSERT ON keep_alive
    FOR EACH STATEMENT EXECUTE FUNCTION trim_keep_alive();
