import os
import requests

def th_finder():
    directory = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(directory):
        if filename.endswith(".th"):
            return filename
            break
    print("no .th found")

def extract_centerline(therion_filename):
    centerline_data = []
    in_centerline_block = False

    with open(therion_filename, 'r') as file:
        for line in file:
            line = line.strip()  # Remove extra whitespace

            if line == "centerline":
                in_centerline_block = True
            elif line == "endcenterline":
                in_centerline_block = False
            elif in_centerline_block:
                centerline_data.append(line)

    return centerline_data

def write_centerline(centerline_data, output_filename,caveName):
    with open(output_filename, 'a') as file:
        # You might want to add Therion file header information here
        file.write("\nsurvey " + caveName.replace(" ", "") + " -title \"" + caveName + "\"\n")
        file.write("\n  centerline\n")
        for line in centerline_data:
            file.write("    " + line + "\n")
        file.write("  endcenterline\n")
        file.write("endsurvey\n")

def add_th2_filenames(output_filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Script's directory

    with open(output_filename, 'w') as file:  # Open for appending
        for filename in os.listdir(current_dir):
            
            if filename.endswith(".th2"):
                file.write(f"input \"{filename}\"\n")  # Add an "input" line

def find_scraps():
    directory = os.path.dirname(os.path.abspath(__file__))
    plan_scraps = []
    extended_scraps = []
    elevation_scraps = []
    for filename in os.listdir(directory):
        if filename.endswith(".th2"):
            print("scrap search" + filename)
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()

                    if line.startswith("scrap") and "-projection plan" in line:
                        scrap_id = line.split()[1]
                        plan_scraps.append(scrap_id)
                        print("plan scrap found: " + scrap_id)

                    elif line.startswith("scrap") and "-projection extended" in line:
                        scrap_id = line.split()[1]
                        extended_scraps.append(scrap_id)
                        print("extended scrap found: " + scrap_id) 

                    elif line.startswith("scrap") and "-projection elevation" in line:
                        scrap_id = line.split()[1]
                        elevation_scraps.append(scrap_id)
                        print("elevation scrap found: " + scrap_id) 

    print(plan_scraps)
    print(extended_scraps)
    print(elevation_scraps)
    all_scraps = [plan_scraps, extended_scraps, elevation_scraps]

    return all_scraps

def write_maps(output_filename, all_scraps):
    plan_scraps = all_scraps[0]
    extended_scraps = all_scraps[1]
    elevation_scraps = all_scraps[2]

    with open(output_filename, 'a') as file:
        if plan_scraps:
            file.write("\nmap planMap -projection plan\n")
            for scrap in plan_scraps:
                file.write("  " + scrap + "\n")
                print("writing: " + scrap)
            file.write("endmap\n")

        if extended_scraps:
            file.write("\nmap extendedProfMap -projection extended\n")
            for scrap in extended_scraps:
                file.write("  " + scrap + "\n")
                print("writing: " + scrap)
            file.write("endmap\n")

        if elevation_scraps:
            file.write("\nmap elevationProfMap -projection elevation\n")
            for scrap in elevation_scraps:
                file.write("  " + scrap + "\n")
                print("writing: " + scrap)
            file.write("endmap\n")

def download_from_github_permalink(permalink, output_filename=None):
    """Downloads a file from a GitHub permalink and saves it locally.

    Args:
        permalink (str): The URL of the file on GitHub, including the permalink format
            (e.g., https://raw.githubusercontent.com/USER/REPO/BRANCH/PATH/TO/FILE).
        output_filename (str, optional): The name to save the downloaded file as.
            If not provided, the original filename will be used.

    Raises:
        ValueError: If the permalink is invalid or the file cannot be downloaded.
    """

    # Extract filename from permalink (if using raw.githubusercontent.com)
    if "raw.githubusercontent.com" in permalink:
        path_parts = permalink.split("/")
        filename = path_parts[-1]
    else:
        filename = output_filename if output_filename else permalink.split("/")[-1]

    # Create output directory if it doesn't exist
    #os.makedirs(os.path.dirname(filename), exist_ok=True)

    try:
        response = requests.get(permalink, stream=True)
        response.raise_for_status()  # Raise an exception for error statuses

        with open(filename, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"File downloaded successfully: {filename}")


    except (requests.exceptions.RequestException, ValueError) as e:
        raise ValueError(f"Error downloading file from {permalink}: {e}") from e

def replace_keyword_in_file(filename, keyword, new_word):
  """
  Opens a long text file, finds a keyword and changes it to "TEST".

  Args:
    filename: The path to the text file.
    keyword: The keyword to be replaced.
    new_word: The new word to replace the keyword with.
  """

  # Open the file in read and write mode
  with open(filename, "r+") as file:
    # Read the entire file contents into a string
    contents = file.read()

    # Replace all occurrences of the keyword with the new word
    new_contents = contents.replace(keyword, new_word)

    # Move the cursor to the beginning of the file
    file.seek(0)

    # Write the modified content back to the file
    file.write(new_contents)

  print(f"Keyword '{keyword}' replaced with '{new_word}' in {filename}")

# Download compiler and symbolset .thconfig files
# alternatively, copy these files into the folder from a local folder
# could also program a copy-paster from a local path
symbolsetLink = "https://github.com/Greenman126/Christians-Therion-Template/blob/5d172d7021bbcaa05116ee5b403c6673e57f0128/Symbolset_DeCelle.thconfig"
compilerLink = "https://github.com/Greenman126/Christians-Therion-Template/blob/5d172d7021bbcaa05116ee5b403c6673e57f0128/COMPILE.thconfig"
download_from_github_permalink(symbolsetLink)
download_from_github_permalink(compilerLink)

# Usage
caveInput = input("Enter your survey name here: ")
caveName = caveInput.replace(" ", "")

input_filename = th_finder()
new_th_filename = caveName.replace(" ", "") + "_Auto.th"

centerline_data = extract_centerline(input_filename)
add_th2_filenames(new_th_filename)
write_maps(new_th_filename, find_scraps())
write_centerline(centerline_data, new_th_filename, caveName)



keyword = "CAVETH_REPLACEME.th"
replace_keyword_in_file("Symbolset.th2", keyword, output_filename)

wait = input("Press Enter To Close")