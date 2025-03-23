INSERT INTO users (email, hashed_password, token)
VALUES ($1, $2, $3)
RETURNING id, email, token, created_at;
