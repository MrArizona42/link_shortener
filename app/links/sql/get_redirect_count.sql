SELECT COUNT(*) AS total_redirects
FROM redirects
WHERE short_code = $1;
