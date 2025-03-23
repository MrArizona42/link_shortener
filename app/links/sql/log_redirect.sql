-- app/links/sql/log_redirect.sql
INSERT INTO redirects (short_code, user_agent, ip_address)
VALUES ($1, $2, $3);
