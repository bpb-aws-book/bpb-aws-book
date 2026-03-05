CREATE TABLE books_book (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    author VARCHAR(100) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    is_rented BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create a trigger to auto-update the updated_at field
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_book_updated_at
    BEFORE UPDATE ON books_book
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- Insert sample book data
INSERT INTO books_book (name, description, author, price, is_rented) VALUES
('Clean Code: A Handbook of Agile Software Craftsmanship', 'My fav book', 'Robert C Martin', 35.99, FALSE),
('Code Complete: A Practical Handbook of Software Construction', 'One of the best practical guides to programming', 'Steve McConnell', 54.99, FALSE),
('Head First Software Architecture: A Learners Guide to Architectural Thinking', 'Teaches software architecture ', 'Raju Gandhi', 505.99, FALSE),
('The Warren Buffett Way', 'An insightful new take on the life and work of one of the worlds most remarkable investors', 'Robert G. Hagstrom', 54.99, FALSE);
