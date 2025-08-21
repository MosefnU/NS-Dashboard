-- SQLite
SELECT * FROM stations
ORDER BY transaction_count DESC;
SELECT * FROM stations
ORDER BY passenger_count DESC;
SELECT
    A.[ticket id] as TicketID,
    A.[TRANSACTIE ID] as TransactionID1,
    B.[TRANSACTIE ID] as TransactionID2,
    A.station AS start_station,
    B.station AS end_station,
    A.[HEENREIS VERTREKSTATION] AS ticket_start_station_heenreis,
    B.[HEENREIS AANKOMSTSTATION] AS ticket_end_station_heenreis
        FROM transactions A, transactions B
        WHERE
            A.STATION <> '0'
        AND B.STATION <> '0'
        AND A.[ticket id] IS NOT NULL
        AND B.[ticket id] IS A.[ticket id]
        AND A.richting = 'paid'
        AND B.richting = 'unpaid';

SELECT A.[ticket id] AS TicketID,
       A.station AS check_in,
       B.station AS check_uit,
       A.[HEENREIS VERTREKSTATION],
       A.[HEENREIS AANKOMSTSTATION],
       A.[TERUGREIS VERTREKSTATION],
       A.[TERUGREIS AANKOMSTSTATION]
       FROM transactions A, transactions B
       WHERE (
       A.[ticket id] = B.[ticket id]
       AND A.richting = 'unpaid'
       AND B.richting = 'paid')
       AND A.station <> '0'
       AND B.station <> '0'
       ORDER BY A.[TICKET ID], A.[HEENREIS VERTREKSTATION] ASC;

SELECT A.[ticket id] AS TicketID,
        A.[HEENREIS VERTREKSTATION],
       A.[HEENREIS AANKOMSTSTATION],
       A.[TERUGREIS VERTREKSTATION],
       A.[TERUGREIS AANKOMSTSTATION]
       FROM transactions A        
LEFT JOIN (SELECT A.station AS check_in,
            B.station AS check_uit
            FROM transactions A, transactions B
            WHERE A.richting = 'paid'
            AND B.richting = 'unpaid'
        ) C
       ON A.[ticket id] = C.[ticket id]
       ORDER BY A.[TICKET ID], A.[HEENREIS VERTREKSTATION] ASC;

SELECT A.[ticket id] AS TicketID,
       A.station AS check_in,
       C.station AS check_uit,
       A.[HEENREIS VERTREKSTATION],
       A.[HEENREIS AANKOMSTSTATION],
       A.[TERUGREIS VERTREKSTATION],
       A.[TERUGREIS AANKOMSTSTATION]
FROM transactions A
LEFT JOIN (
    SELECT [ticket id], station, RICHTING
    FROM transactions
) C
ON A.[ticket id] = C.[ticket id] and A.RICHTING <> C.RICHTING
WHERE A.RICHTING = 'unpaid' OR NOT EXISTS (
    SELECT *
    FROM transactions B
    WHERE B.[ticket id] = A.[ticket id]
    AND B.richting = 'paid'
)
ORDER BY A.[ticket id], A.[HEENREIS VERTREKSTATION] ASC;

SELECT A.[ticket id] AS TicketID,
       A.station AS check_in,
       B.station AS check_uit,
       A.[HEENREIS VERTREKSTATION],
       A.[HEENREIS AANKOMSTSTATION],
       A.[TERUGREIS VERTREKSTATION],
       A.[TERUGREIS AANKOMSTSTATION]
FROM transactions A, transactions B
WHERE A.RICHTING = 'unpaid' OR NOT EXISTS (
    SELECT *
    FROM transactions C
    WHERE C.[ticket id] = A.[ticket id]
    AND C.richting = 'paid'
)
ORDER BY A.[ticket id], A.[HEENREIS VERTREKSTATION] ASC;

SELECT 
    A.[ticket id] AS TicketID,
    A.station AS check_in,
    B.station AS check_uit,
    A.[HEENREIS VERTREKSTATION],
    A.[HEENREIS AANKOMSTSTATION],
    A.[TERUGREIS VERTREKSTATION],
    A.[TERUGREIS AANKOMSTSTATION]
FROM transactions A
LEFT JOIN transactions B
    ON A.[ticket id] = B.[ticket id]
    AND A.richting <> B.richting
WHERE A.richting = 'unpaid'
  OR NOT EXISTS (
      SELECT 1
      FROM transactions C
      WHERE C.[ticket id] = A.[ticket id]
        AND C.richting = 'paid'
  )
ORDER BY A.[ticket id], A.[HEENREIS VERTREKSTATION] ASC;

SELECT 
    A.[ticket id] AS TicketID,
    A.station AS check_in,
    B.station AS check_uit,
    A.[HEENREIS VERTREKSTATION],
    A.[HEENREIS AANKOMSTSTATION],
    A.[TERUGREIS VERTREKSTATION],
    A.[TERUGREIS AANKOMSTSTATION]
FROM transactions A
LEFT JOIN transactions B
    ON A.[ticket id] = B.[ticket id]
    AND A.richting <> B.richting
WHERE A.richting = 'unpaid'
  OR NOT EXISTS (
      SELECT 1
      FROM transactions C
      WHERE C.[ticket id] = A.[ticket id] AND C.richting = 'unpaid'
  )
ORDER BY A.[ticket id], A.[HEENREIS VERTREKSTATION] ASC;

SELECT * FROM journeys
WHERE check_in = check_uit;
