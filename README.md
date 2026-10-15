# Enterprise Open Data Platform
## Lecture 2 - Docker + Git workflow completed
## Lecture 3 - Created PG DataBases
## Lecture 4 - Created tables and inserted data in PostgreSQL
## Lecture 5 - Inserted historical data, created views, materialized views and indexes
# Lecture 6 - Lecture 6: Data modeling (star schema)
## Lecture 6 - Data Modeling

- Create `analytics` schema with dimension tables: `dim_date`, `dim_location`, `dim_currency`
- Create fact tables: `fact_weather`, `fact_currency`, `fact_seismic`
- Populate fact tables from operational schemas with ETL-lite SQL
- Add cross-domain analytical query joining all three domains via conformed `dim_date`
- Add star schema documentation with Mermaid ER diagram (`docs/star_schema.md`)
- Add SCD Type 2 upsert logic in Python with a 3-scenario test (`src/modeling/scd2.py`)
