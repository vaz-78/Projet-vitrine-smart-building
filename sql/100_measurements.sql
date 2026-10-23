CREATE TABLE measurements (ts TIMESTAMPTZ NOT NULL,
building TEXT NOT NULL,
space TEXT NOT NULL,
point TEXT NOT NULL,
value DOUBLE PRECISION NOT NULL,
unit TEXT NOT NULL
);

SELECT create_hypertable('measurements', by_range('ts'));
