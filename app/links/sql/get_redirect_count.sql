SELECT COUNT(*) AS total_redirects
FROM redirects
WHERE short_code = $1
    and short_code in (SELECT short_code FROM links WHERE owner_email = $2)
GROUP BY short_code;
