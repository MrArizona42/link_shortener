UPDATE links
SET original_url = $1
WHERE short_code = $2
    and owner_email = $3
RETURNING original_url, short_code;
