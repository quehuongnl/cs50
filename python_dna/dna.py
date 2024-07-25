import csv
import sys


def main():
    # TODO: Check for command-line usage
    if len(sys.argv) != 3:
        sys.exit("Usage: python dna.py data.csv sequence.txt")

    # TODO: Read database file into a variable
    dict = []
    with open(sys.argv[1]) as file:
        reader = csv.DictReader(file)
        for row in reader:
            dict.append(row)

    STR = list(dict[0].keys())
    STR.pop(0)
    n = len(STR)

    # TODO: Read DNA sequence file into a variable
    sequence = ""
    with open(sys.argv[2]) as s:
        DNA_sequence = csv.reader(s)
        for row in DNA_sequence:
            for i in row:
                sequence += i

    # TODO: Find longest match of each STR in DNA sequence
    DNA = []
    for i in range(n):
        DNA.append(longest_match(sequence, STR[i]))

    # TODO: Check database for matching profiles
    for item in dict:
        count = 0
        for i in range(n):
            if int(item[STR[i]]) == DNA[i]:
                count += 1
                if count == n:
                    print(item["name"])
                    return sys.exit(0)
            else:
                break
    print("No match")
    return sys.exit(0)


def longest_match(sequence, subsequence):
    """Returns length of longest run of subsequence in sequence."""

    # Initialize variables
    longest_run = 0
    subsequence_length = len(subsequence)
    sequence_length = len(sequence)

    # Check each character in sequence for most consecutive runs of subsequence
    for i in range(sequence_length):
        # Initialize count of consecutive runs
        count = 0

        # Check for a subsequence match in a "substring" (a subset of characters) within sequence
        # If a match, move substring to next potential match in sequence
        # Continue moving substring and checking for matches until out of consecutive matches
        while True:
            # Adjust substring start and end
            start = i + count * subsequence_length
            end = start + subsequence_length

            # If there is a match in the substring
            if sequence[start:end] == subsequence:
                count += 1

            # If there is no match in the substring
            else:
                break

        # Update most consecutive matches found
        longest_run = max(longest_run, count)

    # After checking for runs at each character in seqeuence, return longest run found
    return longest_run


main()
