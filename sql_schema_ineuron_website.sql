-- Create Database
CREATE DATABASE ineuron;

-- Create table into the Database
CREATE TABLE courses (
    id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    PRIMARY KEY (id)
);
