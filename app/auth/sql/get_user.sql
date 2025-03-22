SELECT id, email, created_at
FROM users
WHERE email = $1 and hashed_password = $2
LIMIT 1;
