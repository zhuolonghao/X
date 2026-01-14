/* Teradata SQL SELECT statement for fuzzy matching company names.
Logic:
1. Normalization to lowercase.
2. Stripping of parentheticals and "Public" suffixes.
3. Use of LIKE '[clean_name]%' for prefix fuzzy matching.
*/

SELECT
    cust_id,
    cust_nm,
    segment_nm
FROM
    Customer_Table
WHERE
    --- Industrial & Commercial
    LOWER(cust_nm) LIKE 'texas instruments%'
    OR LOWER(cust_nm) LIKE 'nxp semiconductors%'
    OR LOWER(cust_nm) LIKE 'stmicroelectronics%'
    OR LOWER(cust_nm) LIKE 'infineon technologies%'
    OR LOWER(cust_nm) LIKE 'renesas electronics%'
    OR LOWER(cust_nm) LIKE 'microchip technology%'
    OR LOWER(cust_nm) LIKE 'broadcom%'
    OR LOWER(cust_nm) LIKE 'qualcomm%'
   --- Home & Life
    OR LOWER(cust_nm) LIKE 'nordic semiconductor%'
    OR LOWER(cust_nm) LIKE 'espressif systems%'
    OR LOWER(cust_nm) LIKE 'telink semiconductor%'
    OR LOWER(cust_nm) LIKE 'synaptics%'
    OR LOWER(cust_nm) LIKE 'mediatek%'
    OR LOWER(cust_nm) LIKE 'nxp / stmicro / ti%';