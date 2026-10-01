// ====================================================================
// POWER QUERY (M) EXTRACTION & TRANSFORMATION SCRIPTS
// Connects to PostgreSQL (production) or CSV files (local fallback)
// ====================================================================

// --- DimCategory ---
let
    Source = Csv.Document(File.Contents("data/processed/DimCategory.csv"), [Delimiter=",", Columns=4, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"category_id", type text},
        {"category_name", type text},
        {"description", type text},
        {"target_margin_pct", type number}
    })
in
    #"Changed Type"

// --- DimVendor ---
let
    Source = Csv.Document(File.Contents("data/processed/DimVendor.csv"), [Delimiter=",", Encoding=65001]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"vendor_id", type text},
        {"vendor_code", type text},
        {"vendor_name", type text},
        {"vendor_category", type text},
        {"contact_person", type text},
        {"email", type text},
        {"phone", type text},
        {"country", type text},
        {"rating", type number},
        {"contract_start_date", type date},
        {"payment_terms", type text},
        {"status", type text}
    })
in
    #"Changed Type"

// --- DimProduct ---
let
    Source = Csv.Document(File.Contents("data/processed/DimProduct.csv"), [Delimiter=",", Encoding=65001]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"product_id", type text},
        {"product_code", type text},
        {"product_name", type text},
        {"category_id", type text},
        {"subcategory", type text},
        {"standard_cost", type number},
        {"selling_price", type number},
        {"status", type text}
    })
in
    #"Changed Type"

// --- DimDate ---
let
    Source = Csv.Document(File.Contents("data/processed/DimDate.csv"), [Delimiter=",", Encoding=65001]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"date_id", Int64.Type},
        {"date", type date},
        {"year", Int64.Type},
        {"quarter", type text},
        {"month_num", Int64.Type},
        {"month_name", type text},
        {"month_year", type text},
        {"is_weekend", type logical}
    })
in
    #"Changed Type"

// --- FactPurchases ---
let
    Source = Csv.Document(File.Contents("data/processed/FactPurchases.csv"), [Delimiter=",", Encoding=65001]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"purchase_id", type text},
        {"vendor_id", type text},
        {"product_id", type text},
        {"purchase_date", type date},
        {"quantity", Int64.Type},
        {"unit_purchase_price", type number},
        {"total_purchase_value", type number}
    })
in
    #"Changed Type"

// --- FactSales ---
let
    Source = Csv.Document(File.Contents("data/processed/FactSales.csv"), [Delimiter=",", Encoding=65001]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"sale_id", type text},
        {"product_id", type text},
        {"sale_date", type date},
        {"quantity", Int64.Type},
        {"unit_selling_price", type number},
        {"total_sales_value", type number}
    })
in
    #"Changed Type"
