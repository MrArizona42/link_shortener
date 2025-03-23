SELECT original_url
FROM links
WHERE short_code = $1
    and expires_at > now()
LIMIT 1;
