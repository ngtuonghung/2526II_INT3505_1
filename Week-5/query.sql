CREATE TABLE authors (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(150) NOT NULL,
    bio        TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE books (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    title          VARCHAR(255) NOT NULL,
    author_id      INT REFERENCES authors(id),
    category_id    INT REFERENCES categories(id),
    published_year INT,
    available      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE members (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email     VARCHAR(150) UNIQUE NOT NULL,
    phone     VARCHAR(20),
    role      ENUM('admin', 'member')     DEFAULT 'member',
    status    ENUM('active', 'suspended') DEFAULT 'active',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id        INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL REFERENCES members(id),
    book_id   INT NOT NULL REFERENCES books(id),
    status    ENUM('reserved', 'borrowed', 'returned', 'cancelled', 'overdue')
              NOT NULL DEFAULT 'reserved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_at     TIMESTAMP NULL
);

INSERT INTO authors (name, bio) VALUES
('Nguyễn Nhật Ánh', 'Nhà văn người Việt Nam nổi tiếng với các tác phẩm thiếu nhi và tuổi teen.');

INSERT INTO categories (name) VALUES
('Văn học Việt Nam');

INSERT INTO members (full_name, email, phone, role) VALUES
('Trần Quản Trị',  'admin@library.com', '0901000001', 'admin'),
('Lê Văn Người Dùng', 'user@library.com',  '0901000002', 'member');

INSERT INTO books (title, author_id, category_id, published_year) VALUES
('Tôi thấy hoa vàng trên cỏ xanh',  1, 1, 1991),
('Mắt biếc',                         1, 1, 1990),
('Cho tôi xin một vé đi tuổi thơ',   1, 1, 2008),
('Đảo mộng mơ',                      1, 1, 2002),
('Kính vạn hoa - Tập 1',             1, 1, 1995),
('Kính vạn hoa - Tập 2',             1, 1, 1995),
('Kính vạn hoa - Tập 3',             1, 1, 1996),
('Ngồi khóc trên cây',               1, 1, 2013),
('Lá nằm trong lá',                  1, 1, 2011),
('Có hai con mèo ngồi bên cửa sổ',   1, 1, 2012),
('Tâm hồn quê hương',                1, 1, 1986),
('Trại hoa vàng',                    1, 1, 1994),
('Bong bóng lên trời',               1, 1, 1993),
('Còn chút gì để nhớ',               1, 1, 2014),
('Út Quyên và tôi',                  1, 1, 2010),
('Con chó nhỏ mang giỏ hoa hồng',    1, 1, 2016),
('Người Quảng đi ăn mì Quảng',       1, 1, 2020),
('Quán gò đi lên',                   1, 1, 1990),
('Cô gái đến từ hôm qua',            1, 1, 1989),
('Bầy chim chìa vôi',                1, 1, 1993);

INSERT INTO transactions (member_id, book_id, status, due_at) VALUES
(2, 1, 'reserved', NULL),
(2, 2, 'borrowed', NOW() + INTERVAL 14 DAY),
(2, 3, 'returned', NOW() - INTERVAL 3 DAY),
(2, 4, 'overdue',  NOW() - INTERVAL 7 DAY);

SELECT * FROM transactions
JOIN books ON transactions.book_id = books.id;