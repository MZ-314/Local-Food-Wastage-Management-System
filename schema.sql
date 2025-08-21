PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS providers (
  Provider_ID   INTEGER PRIMARY KEY,
  Name          TEXT NOT NULL,
  Type          TEXT NOT NULL,
  Address       TEXT,
  City          TEXT,
  Contact       TEXT
);

CREATE TABLE IF NOT EXISTS receivers (
  Receiver_ID   INTEGER PRIMARY KEY,
  Name          TEXT NOT NULL,
  Type          TEXT NOT NULL,
  City          TEXT,
  Contact       TEXT
);

CREATE TABLE IF NOT EXISTS food_listings (
  Food_ID       INTEGER PRIMARY KEY,
  Food_Name     TEXT NOT NULL,
  Quantity      INTEGER NOT NULL CHECK (Quantity >= 0),
  Expiry_Date   DATE NOT NULL,
  Provider_ID   INTEGER NOT NULL,
  Provider_Type TEXT NOT NULL,
  Location      TEXT NOT NULL,
  Food_Type     TEXT NOT NULL,
  Meal_Type     TEXT NOT NULL,
  FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID)
);

CREATE TABLE IF NOT EXISTS claims (
  Claim_ID    INTEGER PRIMARY KEY,
  Food_ID     INTEGER NOT NULL,
  Receiver_ID INTEGER NOT NULL,
  Status      TEXT NOT NULL,
  Timestamp   DATETIME NOT NULL,
  FOREIGN KEY (Food_ID) REFERENCES food_listings(Food_ID),
  FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID)
);
