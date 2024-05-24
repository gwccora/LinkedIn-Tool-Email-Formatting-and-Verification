import csv

def delete_rows_with_linkedin(filename):
    # Read the CSV file and store its content in a list
    rows_to_keep = []
    with open(filename, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # Check if the first column contains the word "LinkedIn"
            if "LinkedIn" not in row[0]:
                rows_to_keep.append(row)

    # Write the filtered content back to the CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows_to_keep)

# Example usage:
filename = "attemaillist.csv"
delete_rows_with_linkedin(filename)
