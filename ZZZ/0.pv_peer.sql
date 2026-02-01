SELECT
    cust_id,
    cust_nm,
    addr_line_1_txt,
    city_nm,
    st_cd
FROM
    dw_tables.customer_dimension
WHERE
    LOWER(cust_nm) LIKE 'andersen%'
    OR LOWER(cust_nm) LIKE 'pella%'
    OR LOWER(cust_nm) LIKE 'marvin%'
    OR LOWER(cust_nm) LIKE 'masonite%'
    OR LOWER(cust_nm) LIKE 'therma-tru%'
    OR LOWER(cust_nm) LIKE 'thermatru%'
    OR LOWER(cust_nm) LIKE 'ply gem%'
    OR LOWER(cust_nm) LIKE 'ply-gem%'
    OR LOWER(cust_nm) LIKE 'milgard%'
    OR LOWER(cust_nm) LIKE 'owens corning%'
    OR LOWER(cust_nm) LIKE 'fortune brands%'
    OR LOWER(cust_nm) LIKE 'builders firstsource%'
    OR LOWER(cust_nm) LIKE 'builders first source%';