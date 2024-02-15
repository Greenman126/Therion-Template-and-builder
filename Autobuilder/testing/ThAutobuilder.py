import os
import requests

def th_finder():
    directory = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(directory):
        if filename.endswith(".th"):
            return filename
            break
    print("no .th found")

def write_survey_heading(output_filename, caveName):
    with open(output_filename, 'w') as file:
        # You might want to add Therion file header information here
        file.write("#This .th file was autogenerated with a script created by Christian DeCelle\n")
        file.write("\nsurvey " + caveName.replace(" ", "") + " -title \"" + caveName + "\"\n")

def write_endsurvey(output_filename):
    with open(output_filename, 'a') as file:
        # You might want to add Therion file header information here
        file.write("\nendsurvey\n")

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
        file.write("\n  centerline\n")
        for line in centerline_data:
            file.write("    " + line + "\n")
        file.write("  endcenterline\n")

def add_th2_filenames(output_filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Script's directory

    with open(output_filename, 'a') as file:  # Open for appending
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
            print("Searching for scraps in: " + filename)
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

def write_maps(output_filename, scrapsList):
    plan_scraps = scrapsList[0]
    extended_scraps = scrapsList[1]
    elevation_scraps = scrapsList[2]

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

def write_th(input_th, new_th_filename, caveName, scrapsList):
    write_survey_heading(new_th_filename, caveName)
    centerline_data = extract_centerline(input_th)
    add_th2_filenames(new_th_filename)
    write_centerline(centerline_data, new_th_filename, caveName)
    scrapsLists = find_scraps()
    write_maps(new_th_filename, scrapsList)
    write_endsurvey(new_th_filename)

def download_from_github_permalink(url, save_path=None):
    """Downloads a file from a GitHub permalink and saves it locally.

    Args:
        url (str): The GitHub permalink to the file.
        save_path (str, optional): The path where the file should be saved.
            If not provided, the filename will be extracted from the URL
            and used as the save path. Defaults to None.

    Returns:
        str: The path to the downloaded file.

    Raises:
        ValueError: If the URL is invalid.
        requests.exceptions.RequestException: If there's an error downloading the file.
        OSError: If there's an error saving the file.
    """

    if not url.startswith("https://"):
        raise ValueError("Invalid URL: must start with https://")

    # Extract filename from permalink (excluding GitHub branding)
    filename = os.path.basename(url.split("/")[-2])

    if save_path is None:
        save_path = filename

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Use a context manager for reliable file creation and closing
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"File downloaded successfully: {save_path}")
        return save_path

    except (ValueError, requests.exceptions.RequestException) as e:
        print(f"Error downloading file: {e}")
        return None

def createFolder(newFolderName):
    # Get the current working directory (where the script is located)
    current_dir = os.getcwd()

    # Create the output folder path
    output_dir = os.path.join(current_dir, newFolderName)

    # Create the folder, handling potential errors gracefully
    try:
        os.makedirs(output_dir)
        print("Folder 'output' created successfully!")
    except FileExistsError:
        print("Folder 'output' already exists.")
    except OSError as err:
        print("Error creating folder:", err)

def returnExportString(projection, layout, scale, caveName, filetype):
    return ("export map -projection " + projection + " -layout " + layout + " -layout-scale 1 " + scale + " -o \"output/" + caveName + "+WORKING_Plan_Scale" + scale + "." + filetype + "\"\n")


def add_exports_thconfig(compilerRename, caveName, scrapsList):
    plan_scraps = scrapsList[0]
    extended_scraps = scrapsList[1]
    elevation_scraps = scrapsList[2]
    planLayout1 = "workingPlan"
    scale = ["100", "200", "800"]
    print("Adding exporting lines...")

    with open(compilerRename, 'a') as file:
        file.write("####THAUTOBUILD EXPORT GENERATION BELOW#####")
        if plan_scraps:
            print("Adding plan exports...")
            file.write("##Plan Maps Below##")
            for s in scale:
                file.write(returnExportString("plan", planLayout1, s, caveName, "pdf"))
                file.write(returnExportString("plan", planLayout1, s, caveName, "svg"))

        if extended_scraps:
            print("Adding extended exports...")
            file.write("\nmap extendedProfMap -projection extended\n")

        if elevation_scraps:
            print("Adding elevation exports...")
            file.write("\nmap elevationProfMap -projection elevation\n")

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




# Usage
suffix = "_Auto" #can be changed to adjust suffic to files

caveInput = input("Enter your survey name here: ")
caveName = caveInput.replace(" ", "")

input_th = th_finder() #Grabs first .th file in the folder that doesn't end in 
new_th_filename = caveName.replace(" ", "") + suffix + ".th" #removes whitespaces in the inpput filename, adds a suffix and the .th extension

# Download compiler and symbolset .thconfig files
# alternatively, copy these files into the folder from a local folder
# could also program a copy-paster from a local path
symbolsetLink = "https://raw.githubusercontent.com/Greenman126/Christians-Therion-Template/main/Symbolset_DeCelle.thconfig"
symbolsetRename = "Symbolset_DeCelle.thconfig" #renames output symbolset if wanted

compilerLink = "https://raw.githubusercontent.com/Greenman126/Christians-Therion-Template/main/COMPILE.thconfig"
compilerRename = "COMPILE_" + caveName + ".thconfig" #Adds suffix to compiler

download_from_github_permalink(symbolsetLink, symbolsetRename)
download_from_github_permalink(compilerLink, compilerRename)

scrapsList = find_scraps()
write_th(input_th, new_th_filename, caveName, scrapsList)

#Modify the thconfig file
print("Modifying thconfig")

add_exports_thconfig(compilerRename, caveName, scrapsList) #Writes export lines to the COMPILE.thconfig file if that type of scrap was exported
th_replacement_keyword = "CAVETH_REPLACEME.th" #references the keyword in the COMPILE file to be replaced
replace_keyword_in_file(compilerRename, th_replacement_keyword, new_th_filename)

createFolder("output") #creates output folder for when you export compile the sketches

wait = input("Press Enter To Close")