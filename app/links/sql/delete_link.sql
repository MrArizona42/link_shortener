DELETE
FROM links
WHERE short_code = $1
    AND owner_email = $2
RETURNING original_url, short_code;
