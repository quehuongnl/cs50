import csv
import requests


def main():
    # Read NYTimes Covid Database
    download = requests.get(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"
    )
    decoded_content = download.content.decode("utf-8")
    file = decoded_content.splitlines()
    reader = csv.DictReader(file)

    # Construct 14 day lists of new cases for each states
    new_cases = calculate(reader)

    # Create a list to store selected states
    states = []
    print("Choose one or more states to view average COVID cases.")
    print("Press enter when done.\n")

    while True:
        state = input("State: ")
        if state in new_cases:
            states.append(state)
        if len(state) == 0:
            break

    print(f"\nSeven-Day Averages")

    # Print out 7-day averages for this week vs last week
    comparative_averages(new_cases, states)


# TODO: Create a dictionary to store 14 most recent days of new cases by state
def calculate(reader):
    new_cases = {}
    previous_cases = {}

    for row in reader:
        state = row["state"]
        date = row["date"]
        cases = int(row["cases"])

        if state not in new_cases:
            new_cases[state] = []
        else:
            new_cases[state].append(cases - previous_cases[state])

        previous_cases[state] = cases

        if len(new_cases[state]) > 14:
            new_cases[state].pop(0)

    return new_cases


# TODO: Calculate and print out seven day average for given state
def comparative_averages(new_cases, states):
    for state in states:
        week_average = round(sum(new_cases[state][7:]) / 7)
        last_average = round(sum(new_cases[state][:7]) / 7)
        change = week_average - last_average

        if change > 0:
            trend = "an increase"
        else:
            trend = "a decrease"

        try:
            percent = round(abs((change / last_average)) * 100)
        except ZeroDivisionError:
            raise ZeroDivisionError
        else:
            print(
                "{} had a 7-day average of {} and {} of {}%.".format(
                    state, week_average, trend, percent
                )
            )


main()
