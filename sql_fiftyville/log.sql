-- Keep a log of any SQL queries you execute as you solve the mystery.
-- look for a crime scene report that matches the date and the location of the crime
-- July 28, 2021 and Humphrey Street
SELECT * FROM crime_scene_reports
    WHERE year = 2021 AND month = 7 AND day = 28 AND street = 'Humphrey Street';

-- see interviews of 3 witnesses
SELECT * FROM interviews
    WHERE year = 2021 AND month = 7 AND day = 28;

-- see logs at the bakery around 10am to find car of the thief
SELECT name FROM people WHERE license_plate IN
    (SELECT license_plate FROM bakery_security_logs
        WHERE year = 2021 AND month = 7 AND day = 28 AND hour = 10)
        ORDER BY name;

-- find ATM transactions of the thief
SELECT name FROM atm_transactions
    JOIN bank_accounts ON bank_accounts.account_number = atm_transactions.account_number
    JOIN people ON bank_accounts.person_id = people.id
        WHERE year = 2021 AND month = 7 AND day = 28 AND transaction_type = 'withdraw' AND atm_location = 'Leggett Street'
        ORDER BY name;

-- find location of the earliest flight out of town tomorrow
SELECT * FROM flights JOIN airports ON airports.id = flights.destination_airport_id
    WHERE year = 2021 AND month = 7 AND day = 29;

-- find passenger on the flight id 36 to New York City
SELECT name FROM flights
    JOIN passengers ON flights.id = passengers.flight_id
    JOIN people ON passengers.passport_number = people.passport_number
        WHERE flights.id = 36 ORDER BY name;

-- find caller of phone call at Bakery in: Bruce, Luca, Taylor
SELECT receiver, name FROM phone_calls
    JOIN people ON phone_calls.receiver = people.phone_number
        WHERE year = 2021 AND month = 7 AND day = 28
        AND caller in (SELECT phone_number FROM people WHERE name = 'Bruce' or name = 'Kenny' or name = 'Luca' or name = 'Taylor');