UPDATE users
SET token = $2,
    updated_at = NOW()
WHERE email = $1
RETURNING id, email, token, updated_at;
