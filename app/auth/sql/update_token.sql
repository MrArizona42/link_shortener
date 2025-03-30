UPDATE users
SET token = $2,
    updated_at = NOW()
WHERE email = $1
RETURNING id, email, token, created_at, updated_at;
