SELECT original_url
FROM links
WHERE short_code = $1
LIMIT 1;
