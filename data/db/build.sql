CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "$"
);

CREATE TABLE IF NOT EXISTS jackpot (
	Jackpot integer PRIMARY KEY,
	Amount integer DEFAULT 50
);

-- INSERT INTO jackpot
-- VALUES (0, 50);

DROP TABLE ledger;

CREATE TABLE IF NOT EXISTS ledger (
	UserID integer PRIMARY KEY, 
	UserText text,
	KC integer DEFAULT 0,
	Level integer DEFAULT 0,
	Mined integer DEFAULT 0,
	Gambles integer Default 10,
	Duel integer Default 0,
	Lock text DEFAULT CURRENT_TIMESTAMP
);

-- ALTER TABLE ledger
-- ADD Gambles integer DEFAULT 10;

-- UPDATE ledger
-- SET KC = 1000
-- WHERE UserID = 61330577730576384;