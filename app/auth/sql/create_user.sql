-- app/auth/sql/create_user.sql
INSERT INTO users (email, hashed_password)
VALUES ($1, $2)
RETURNING id, email;
