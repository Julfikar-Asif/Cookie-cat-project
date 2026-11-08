let
    Source = Csv.Document(
        File.Contents("D:\cookie-cat\data\cookie_cats.csv"),
        [Delimiter = ",", Columns = 5, Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    TypedColumns = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"userid", Int64.Type},
            {"version", type text},
            {"sum_gamerounds", Int64.Type},
            {"retention_1", type logical},
            {"retention_7", type logical}
        }
    ),
    FilteredOutlier = Table.SelectRows(TypedColumns, each [sum_gamerounds] < 40000),
    AddedSegment = Table.AddColumn(
        FilteredOutlier,
        "Segment",
        each
            if [sum_gamerounds] = 0 then "0 rounds"
            else if [sum_gamerounds] <= 10 then "1-10"
            else if [sum_gamerounds] <= 50 then "11-50"
            else if [sum_gamerounds] <= 200 then "51-200"
            else "200+",
        type text
    ),
    AddedSegmentOrder = Table.AddColumn(
        AddedSegment,
        "SegmentOrder",
        each
            if [sum_gamerounds] = 0 then 1
            else if [sum_gamerounds] <= 10 then 2
            else if [sum_gamerounds] <= 50 then 3
            else if [sum_gamerounds] <= 200 then 4
            else 5,
        Int64.Type
    ),
    ReorderedColumns = Table.ReorderColumns(
        AddedSegmentOrder,
        {"userid", "version", "Segment", "SegmentOrder", "sum_gamerounds", "retention_1", "retention_7"}
    )
in
    ReorderedColumns
