INSERT INTO links (original_url, short_code, owner_email)
VALUES ($1, $2, $3)
ON CONFLICT (short_code) DO NOTHING
RETURNING short_code;
