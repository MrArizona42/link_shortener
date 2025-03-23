INSERT INTO links (original_url, short_code, owner_email, expires_at)
VALUES ($1, $2, $3, COALESCE($4, NOW() + INTERVAL '7 days'))
ON CONFLICT (short_code) DO NOTHING
RETURNING short_code;
