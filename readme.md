Memelang.net | (c) HOLTWORK LLC | Patents Pending

	CREATE TABLE IF NOT EXISTS meme (rid TEXT, alp TEXT, amt NUMERIC(18, 6), bid BIGINT);
	CREATE INDEX IF NOT EXISTS meme_rid_idx ON meme ((LOWER(rid)));
	CREATE INDEX IF NOT EXISTS meme_alp_idx ON meme ((LOWER(alp))) WHERE alp IS NOT NULL;
	CREATE INDEX IF NOT EXISTS meme_amt_idx ON meme (amt) WHERE amt IS NOT NULL;
	CREATE INDEX IF NOT EXISTS meme_bid_idx ON meme (bid);
	ALTER TABLE meme ADD CONSTRAINT alp_xor_amt CHECK ((alp IS NOT NULL) <> (amt IS NOT NULL));
