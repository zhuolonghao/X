SELECT *
FROM [TARGET_TABLE]
WHERE (
    -- Home & Outdoor Segment
    LOWER(legal_name) LIKE 'lifetime brands%'
    OR LOWER(legal_name) LIKE 'breville%'
    OR LOWER(legal_name) LIKE 'corning%'
    OR LOWER(legal_name) LIKE 'progressive international%'
    OR LOWER(legal_name) LIKE 'meyer%'
    OR LOWER(legal_name) LIKE 'newell brands%'
    OR LOWER(legal_name) LIKE 'simple human%'
    OR LOWER(legal_name) LIKE 'yeti%'
    OR LOWER(legal_name) LIKE 'bradshaw international%'
    OR LOWER(legal_name) LIKE 'pmi worldwide%'
    OR LOWER(legal_name) LIKE 'patagonia%'
    OR LOWER(legal_name) LIKE 'gregory mountain%'
    OR LOWER(legal_name) LIKE 'camelbak%'
    OR LOWER(legal_name) LIKE 'the north face%'
    OR LOWER(legal_name) LIKE 'deuter%'
    OR LOWER(legal_name) LIKE 'cotopaxi%'
    OR LOWER(legal_name) LIKE 'thule%'
    OR LOWER(legal_name) LIKE 'trove brands%'
    
    -- Beauty & Wellness Segment
    OR LOWER(legal_name) LIKE 'conair%'
    OR LOWER(legal_name) LIKE 'spectrum brands%'
    OR LOWER(legal_name) LIKE 'coty%'
    OR LOWER(legal_name) LIKE 'dyson%'
    OR LOWER(legal_name) LIKE 'l''oréal%' -- Escaped apostrophe
    OR LOWER(legal_name) LIKE 'loreal%'   -- Non-apostrophe version
    OR LOWER(legal_name) LIKE 'devacurl%'
    OR LOWER(legal_name) LIKE 'sharkninja%'
    OR LOWER(legal_name) LIKE 'exergen%'
    OR LOWER(legal_name) LIKE 'omron healthcare%'
    OR LOWER(legal_name) LIKE 'crane engineering%'
    OR LOWER(legal_name) LIKE 'lasko products%'
    OR LOWER(legal_name) LIKE 'vesync%'
    OR LOWER(legal_name) LIKE 'the clorox company%'
    OR LOWER(legal_name) LIKE 'zero technologies%'
    OR LOWER(legal_name) LIKE 'vornado air circulation%'
    OR LOWER(legal_name) LIKE 'unilever%'
    OR LOWER(legal_name) LIKE 'wella operations%'
    OR LOWER(legal_name) LIKE 'kiss usa%'
    OR LOWER(legal_name) LIKE 'guardian technologies%'
);