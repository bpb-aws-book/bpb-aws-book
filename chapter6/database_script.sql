/*connect to DB*/
psql --host=<database endpoint> --port=5432 --dbname=<databasename> --username=<user name>

/*Supply password*/

/*perform a select*/
Select * from "books_book";

/* Add a test record*?
INSERT INTO "books_book" 
("id","name", "description", "author", "price", "is_rented", "created_at", "updated_at")
values
(5,'Test','Test','Test',10.0,false,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);


