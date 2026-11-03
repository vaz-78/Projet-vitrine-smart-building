\getenv mdp POSTGRES_PASSWORD_GRAFANA

CREATE ROLE grafana_reader LOGIN PASSWORD :'mdp';
GRANT CONNECT ON DATABASE building_twin TO grafana_reader;
GRANT USAGE ON SCHEMA public TO grafana_reader;
GRANT SELECT ON TABLE measurements TO grafana_reader;