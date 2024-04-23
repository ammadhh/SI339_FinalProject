PRAGMA foreign_keys = ON;

INSERT INTO users(username, fullname, email, filename, password)
VALUES 
('ammadh', 'Ammad Hassan', 'ammad@umich.edu', 'panda.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8'),
('tomato', 'Food Tomato', 'tomato@umich.edu', 'tomato.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8'),
('umichSI', 'SI iscool', 'SI@umich.edu', 'umsi.jpg', 'sha512$a45ffdcc71884853a2cba9e6bc55e812$c739cef1aec45c6e345c8463136dc1ae2fe19963106cf748baf87c7102937aa96928aa1db7fe1d8da6bd343428ff3167f4500c8a61095fb771957b4367868fb8');

INSERT INTO posts(filename, owner)
VALUES
('dog.jpg', 'ammadh'),
('umsi.jpg', 'ammadh');

INSERT INTO comments(owner, postid, text)
VALUES 
('tomato', 2, 'Wow I love SI, SI339 is my favorite class, we should become SI majors :0'),
('ammadh', 1, 'Wow I love your dog!'),
('tomato', 1, 'he looks ready to eat some tomatoes'),
('ammadh', 1, 'Sick dog bro'),
('tomato', 1, 'our dogs should hangout together');

INSERT INTO following(username1, username2)
VALUES
('ammadh', 'tomato'),
('tomato', 'ammadh');

INSERT INTO likes(owner, postid)
VALUES
('tomato', 1),
('ammadh', 1);