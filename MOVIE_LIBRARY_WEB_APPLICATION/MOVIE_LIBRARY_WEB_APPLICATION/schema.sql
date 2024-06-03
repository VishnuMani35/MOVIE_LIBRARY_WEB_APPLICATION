CREATE TABLE IF NOT EXISTS users (
    S_no INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(1000),
    email VARCHAR(1000),
    password VARCHAR(1000)
);

CREATE Table usersTable (
    S_no INT PRIMARY KEY AUTO_INCREMENT,
    movies LONGTEXT,
    watchlist_name VARCHAR(1000)
);