initial_migration_script = """
CREATE TABLE "user" (
	id serial PRIMARY KEY,
	name VARCHAR (255) UNIQUE NOT NULL,
	created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE "user" IS 'Table to store users.';


CREATE TABLE feed (
	id serial PRIMARY KEY,
	uri VARCHAR (255) UNIQUE NOT NULL,
	stalled BOOLEAN DEFAULT false NOT NULL
);
COMMENT ON COLUMN feed.stalled is 'Feed marked as "stalled" after several unsuccessful feed requests.';
COMMENT ON TABLE feed IS 'Table to store feeds.';

CREATE TABLE followed_feed (
	id serial PRIMARY KEY,
	user_id INT NOT NULL,
	feed_id INT NOT NULL,
	FOREIGN KEY (user_id)
      REFERENCES "user" (id),
    FOREIGN KEY (feed_id)
      REFERENCES feed (id)
);

COMMENT ON TABLE followed_feed IS 'Followed feeds by users.';

CREATE TABLE feed_item (
	id serial PRIMARY KEY,
	title TEXT NOT NULL,
	link TEXT NOT NULL,
	description TEXT NOT NULL,
	pub_date TIMESTAMPTZ NOT NULL,
	feed_id INT NOT NULL,
    FOREIGN KEY (feed_id)
      REFERENCES feed (id)
);

COMMENT ON TABLE feed_item IS 'Feed items table.';


CREATE TABLE read_item (
	id serial PRIMARY KEY,
	item_id INT NOT NULL,
	user_id INT NOT NULL,
    FOREIGN KEY (item_id)
      REFERENCES feed_item (id),
    FOREIGN KEY (user_id)
      REFERENCES "user" (id),
    UNIQUE (item_id, user_id)
);

COMMENT ON TABLE read_item IS 'Items marked "read" by users.';

CREATE TABLE registered_feeds (
	id serial PRIMARY KEY,
	feed_id INT NOT NULL,
	user_id INT NOT NULL,
    FOREIGN KEY (feed_id)
      REFERENCES feed (id),
    FOREIGN KEY (user_id)
      REFERENCES "user" (id),
    UNIQUE (feed_id, user_id)
);

COMMENT ON TABLE registered_feeds IS 'Feeds registered by users.';


CREATE INDEX user_name_idx ON "user" (name);
CREATE INDEX feed_uri_idx ON feed (uri);

"""
