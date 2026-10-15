-- dim_location-ის SCD Type 2 ვერსია — 3 დამატებითი სვეტი ისტორიის თვალყურის დევნებისთვის
ALTER TABLE analytics.dim_location
ADD COLUMN valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
ADD COLUMN valid_to DATE,
ADD COLUMN is_current BOOLEAN NOT NULL DEFAULT TRUE;
 
-- fact table-ებში surrogate key-ის ნაცვლად ახლა კონკრეტული 'ვერსიის' location_key-ზე
-- ვჯოინდებით (Fact ისტორიულ მდგომარეობას 'ჩაიკეტავს' ჩაწერის მომენტში).
