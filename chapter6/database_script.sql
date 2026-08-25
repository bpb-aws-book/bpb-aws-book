/*
 * NOTE: This file is a reference of commands to run interactively, not a
 * runnable script. Do NOT execute it directly (for example with
 * "psql -f database_script.sql"), because the first line is a shell command
 * used to connect to the database, not SQL.
 *
 * Instead, follow these steps:
 *   1. Copy the psql connection command below, replace the placeholders
 *      (<database endpoint>, <databasename>, <user name>), and run it in the
 *      Session Manager shell. Supply the password when prompted.
 *   2. Once connected, copy and paste the SQL statements one at a time at the
 *      psql prompt.
 */
/* Connect to the database (run in the shell, not in psql) */
psql --host=<database endpoint> --port=5432 --dbname=<databasename> --username=<user name>

/* Supply the password when prompted */

/* Perform a select */
Select * from "books_book";

/* Add a test record */
INSERT INTO "books_book"
("id","name", "description", "author", "price", "is_rented", "created_at", "updated_at")
values
(5,'Test','Test','Test',10.0,false,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
