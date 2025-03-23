UPDATE links
SET original_url = $1
WHERE short_code = $2
RETURNING original_url, short_code;
