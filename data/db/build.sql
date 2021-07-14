CREATE TABLE IF NOT EXISTS guilds (
	GuildID integer PRIMARY KEY,
	Prefix text DEFAULT "!"
);

CREATE TABLE IF NOT EXISTS jackpot (
	Jackpot integer PRIMARY KEY,
	Amount integer DEFAULT 50
);

--INSERT INTO jackpot
--VALUES (0, 50);

CREATE TABLE IF NOT EXISTS ledger (
	UserID integer PRIMARY KEY, 
	UserText text,
	KC integer DEFAULT 0,
	Level integer DEFAULT 0,
	KCLock text DEFAULT CURRENT_TIMESTAMP
);