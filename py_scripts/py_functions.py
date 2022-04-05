import re
import pandas as pd
import os
import fnmatch

#################################################################################################

# PREPROCESSING: remove html tags
def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    onlybold = re.sub(r"<B>", '#', text)
    clean = re.compile('<.*?>')
    return re.sub(clean, '', onlybold)

#################################################################################################

# PREPROCESSING: code example of the preprocessing task done on the txt files retrieved through scraping
# The following function is specific to the January transcripts (see arguments of the first "if" statement),
# but can be used for all the transcripts of the trial. 

def preprocessing_transctipts_text(directory, df):

    for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename, 'jan*.txt'):
            print(filename)
            fh = open(filename, "r")
            content_html = fh.read()
            content_html = remove_html_tags(content_html)
            content_html = content_html.upper()
            fh.close()
                    
            fh = open("text_notags.txt", "w")
            fh.write(content_html)
            fh.close()

            fh = open("text_notags.txt", "r")
            lines = fh.readlines()
            fh.close()

                    # Weed out blank lines with filter
            lines = filter(lambda x: not x.isspace(), lines)
            lines = filter(lambda x: not x.startswith('('), lines)
                    # Write
            fh = open("noblankbrack.txt", "w")
            fh.write("".join(lines))
            fh.close()

            # Separate dialogs and description
            fh = open('noblankbrack.txt', 'r')
            content = fh.read()
            dialogs = content.split('SUPERIOR COURT OF THE STATE OF CALIFORNIA')[0]
            description = content.split('SUPERIOR COURT OF THE STATE OF CALIFORNIA')[1]
            description
            fh.close()

            # Store dialogs and the descriptive part of the transcript in two different files
            fh = open("dialogs.txt", "w")
            fh.write(dialogs)
            fh.close()
            fh = open("description.txt", "w")
            fh.write(description)
            fh.close()

            # Eliminate spaces within paragraph referred to the
            # same person talking
            fh = open("dialogs.txt", "r")
            lines_2 = fh.readlines()
            fh.close()

            new_text = list()
            for index, line in enumerate(lines_2):
                if index < len(lines_2)-1:
                    next_line = lines_2[index + 1]
                    if not next_line.startswith(("#")):
                        modified_line = line.strip('\n')
                        new_text.append(modified_line)
                    else:
                        new_text.append(line)
            last_line = lines_2[len(lines_2)-1]    
            new_text.append(last_line)

            my_file = open("nospaces.txt", "w")
            new_file_contents = "".join(new_text)
            my_file.write(new_file_contents)
            my_file.close()

            # Isolate the person speaking and her/his speech
            with open('nospaces.txt', "r") as a_file:
                person = list()
                speeches = list()
                for line in a_file:
                    mymatch = re.search(r'\#.*?\: ', line)
                    if mymatch:
                        stripped_line = mymatch.group(0)
                        p = line.split(stripped_line)[0]
                        s = line.split(stripped_line)[1]
                        person.append(stripped_line)
                        speeches.append(s)

            # Create a data frame
            mydict = {'person': person, 'speech': speeches}
            df1 = pd.DataFrame(mydict)

            # Isolate date and time from the first row (i.e. introduction of the transcript)
            date_search = re.search(r"(([ADFJMNOS]\w*)\s[\d]{1,2},\s[\d]{4}\s)|(([ADFJMNOS]\w*)\s[\d]{1,2}\s[\d]{4}\s)", df1.iloc[0,0])
            time_search = re.search(r"([\d]{1,2}:[\d]{1,2}\s(A.M.|P.M.))", df1.iloc[0,0])
            date = date_search.group(1)
            time = time_search.group(1)
            # Add to df
            df1['date'] = date 
            df1['time'] = time
            ncol = df1.shape[0]
            
            new_row = {'person': 'DESCRIPTION', 'speech': description, 'date': date, 'time': time}
            df1.append(new_row, ignore_index = True)
    # -------------------------------------------------------------------------------------------------

            # Manage witness questioning: SUBSTITUTE 'A: ' WITH THE WITNESS NAME
            nrow = df1.shape[0]

            # find lines where the match occurs
            match_a1 = 'CALLED AS A WITNESS BY'
            match_a2 = 'THE WITNESS ON THE STAND AT THE TIME'
            match_a3 = 'HAVING BEEN PREVIOUSLY SWORN'
            case_w = 0
            # Case 123: some witnesses are interrogated for the first time and others for the second time (resumed) and others are from previous days
            if df1['speech'].str.contains(match_a1).any() and df1['speech'].str.contains(match_a2).any() and df1['speech'].str.contains(match_a3).any():
                matching_points_a1 = df1[df1["speech"].str.contains(match_a1)]
                matching_indexes_a1 = list(matching_points_a1.index)
                matching_points_a2 = df1[df1["speech"].str.contains(match_a2)]
                matching_indexes_a2 = list(matching_points_a2.index)
                matching_points_a3 = df1[df1["speech"].str.contains(match_a3)]
                matching_indexes_a3 = list(matching_points_a3.index) 
                matching_indexes_a1.extend(matching_indexes_a2 + matching_indexes_a3)
                matching_indexes_a1.sort() 
                matching_indexes_all_a = matching_indexes_a1.copy()
                case_w = 123
            # Case 12: some witnesses are interrogated for the first time and others for the second time (resumed)
            elif df1['speech'].str.contains(match_a1).any() and df1['speech'].str.contains(match_a2).any():
                matching_points_a1 = df1[df1["speech"].str.contains(match_a1)]
                matching_indexes_a1 = list(matching_points_a1.index)
                matching_points_a2 = df1[df1["speech"].str.contains(match_a2)]
                matching_indexes_a2 = list(matching_points_a2.index) 
                matching_indexes_a1.extend(matching_indexes_a2)
                matching_indexes_a1.sort() 
                matching_indexes_all_a = matching_indexes_a1.copy()
                case_w = 12
            # Case 13: some witnesses are interrogated for the first time and others from previous days
            elif df1['speech'].str.contains(match_a1).any() and df1['speech'].str.contains(match_a3).any():
                matching_points_a1 = df1[df1["speech"].str.contains(match_a1)]
                matching_indexes_a1 = list(matching_points_a1.index)
                matching_points_a3 = df1[df1["speech"].str.contains(match_a3)]
                matching_indexes_a3 = list(matching_points_a3.index) 
                matching_indexes_a1.extend(matching_indexes_a3)
                matching_indexes_a1.sort() 
                matching_indexes_all_a = matching_indexes_a1.copy()
                case_w = 13
            # Case 23: some witnesses are interrogated for the second time, same day and others from previous days
            elif df1['speech'].str.contains(match_a2).any() and df1['speech'].str.contains(match_a3).any():
                matching_points_a2 = df1[df1["speech"].str.contains(match_a2)]
                matching_indexes_a2 = list(matching_points_a2.index)
                matching_points_a3 = df1[df1["speech"].str.contains(match_a3)]
                matching_indexes_a3 = list(matching_points_a3.index) 
                matching_indexes_a2.extend(matching_indexes_a3)
                matching_indexes_a2.sort() 
                matching_indexes_all_a = matching_indexes_a2.copy()
                case_w = 23
            # Case 1: the witnesses are all interrogated for the first time
            elif df1['speech'].str.contains(match_a1).any():
                matching_points_a1 = df1[df1["speech"].str.contains(match_a1)]
                matching_indexes_a1 = list(matching_points_a1.index)
                matching_indexes_all_a = matching_indexes_a1.copy()
                case_w = 1
            # Case 2: the witnesses are all interrogated for the second time within same day
            elif df1['speech'].str.contains(match_a2).any():
                matching_points_a2 = df1[df1["speech"].str.contains(match_a2)]
                matching_indexes_a2 = list(matching_points_a2.index)
                matching_indexes_all_a = matching_indexes_a2.copy()
                case_w = 2
            # Case 3: the witnesses are all from previous days
            elif df1['speech'].str.contains(match_a3).any():
                matching_points_a3 = df1[df1["speech"].str.contains(match_a3)]
                matching_indexes_a3 = list(matching_points_a3.index)
                matching_indexes_all_a = matching_indexes_a3.copy()
                case_w = 3

            # Create an empty list to store the name of the witnesses       
            witnesses = list()
            if case_w!=0:

            # Substitute 'A:' with the name of the witness testifying
                for i in range(0, len(matching_indexes_all_a)):
                    # CASE 123
                    if case_w == 123: 
                        # Retrieve the name of the witness and add it to the witness list
                        if matching_indexes_all_a[i] in matching_indexes_a2:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("THE WITNESS ON THE STAND")[0]
                        elif matching_indexes_all_a[i] in matching_indexes_a3:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("HAVING BEEN PREVIOUSLY SWORN")[0]
                        else:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("CALLED AS A WITNESS BY")[0]

                        witness_name = before_match.split()[-1:]
                        witnesses.append(witness_name)
                        # Substitute 'A: ' with the name of the witness
                        if i < (len(matching_indexes_all_a) - 1):
                            for row in range(matching_indexes_all_a[i], matching_indexes_all_a[i + 1]):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESSS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                        else: # if i corresponds to the last witness interrogation of the day
                            for row in range(matching_indexes_all_a[i], nrow):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name 
                    # CASE 12
                    elif case_w == 12: 
                        # Retrieve the name of the witness and add it to the witness list
                        if matching_indexes_all_a[i] in matching_indexes_a2:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("THE WITNESS ON THE STAND")[0]
                        else:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("CALLED AS A WITNESS BY")[0]

                        witness_name = before_match.split()[-1:]
                        witnesses.append(witness_name)
                        # Substitute 'A: ' with the name of the witness
                        if i < (len(matching_indexes_all_a) - 1):
                            for row in range(matching_indexes_all_a[i], matching_indexes_all_a[i + 1]):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESSS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                        else: # if i corresponds to the last witness interrogation of the day
                            for row in range(matching_indexes_all_a[i], nrow):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                    # CASE 13
                    elif case_w == 13: 
                        # Retrieve the name of the witness and add it to the witness list
                        if matching_indexes_all_a[i] in matching_indexes_a3:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("HAVING BEEN PREVIOUSLY SWORN")[0]
                        else:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("CALLED AS A WITNESS BY")[0]

                        witness_name = before_match.split()[-1:]
                        witnesses.append(witness_name)
                        # Substitute 'A: ' with the name of the witness
                        if i < (len(matching_indexes_all_a) - 1):
                            for row in range(matching_indexes_all_a[i], matching_indexes_all_a[i + 1]):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESSS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                        else: # if i corresponds to the last witness interrogation of the day
                            for row in range(matching_indexes_all_a[i], nrow):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                    # CASE 23
                    elif case_w == 23: 
                        # Retrieve the name of the witness and add it to the witness list
                        if matching_indexes_all_a[i] in matching_indexes_a3:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("HAVING BEEN PREVIOUSLY SWORN")[0]
                        else:
                            before_match = df1.iloc[matching_indexes_all_a[i], 1].split("THE WITNESS ON THE STAND")[0]

                        witness_name = before_match.split()[-1:]
                        witnesses.append(witness_name)
                        # Substitute 'A: ' with the name of the witness
                        if i < (len(matching_indexes_all_a) - 1):
                            for row in range(matching_indexes_all_a[i], matching_indexes_all_a[i + 1]):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESSS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                        else: # if i corresponds to the last witness interrogation of the day
                            for row in range(matching_indexes_all_a[i], nrow):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name

                    # CASE 1
                    elif case_w == 1:
                        before_match = df1.iloc[matching_indexes_all_a[i], 1].split("CALLED AS A WITNESS BY")[0]
                        witness_name = before_match.split()[-1:]
                        witnesses.append(witness_name)
                        if i < (len(matching_indexes_all_a)-1):
                            for row in range(matching_indexes_all_a[i], matching_indexes_all_a[i + 1]):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                        else:
                            for row in range(matching_indexes_all_a[i], nrow):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                    # CASE 2
                    elif case_w == 2:
                        before_match = df1.iloc[matching_indexes_all_a[i], 1].split("THE WITNESS ON THE STAND")[0]
                        witness_name = before_match.split()[-1:]
                        witnesses.append(witness_name)
                        if i < (len(matching_indexes_all_a)-1):
                            for row in range(matching_indexes_all_a[i], matching_indexes_all_a[i + 1]):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                        else:
                            for row in range(matching_indexes_all_a[i], nrow):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                    # CASE 3
                    elif case_w == 3:
                        before_match = df1.iloc[matching_indexes_all_a[i], 1].split("HAVING BEEN PREVIOUSLY SWORN")[0]
                        witness_name = before_match.split()[-1:]
                        witnesses.append(witness_name)
                        if i < (len(matching_indexes_all_a)-1):
                            for row in range(matching_indexes_all_a[i], matching_indexes_all_a[i + 1]):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
                        else:
                            for row in range(matching_indexes_all_a[i], nrow):
                                if df1.iloc[row, 0] == '#A: ' or df1.iloc[row, 0] == '#THE WITNESS: ':
                                    df1.iloc[row, df1.columns.get_loc('person')] = witness_name
    # -------------------------------------------------------------------------------------------------                        
            
            # Substitute 'Q:' with the name of the attorney questioning
            match_1 = 'CROSS-EXAMINATIONBY'
            match_2 = 'DIRECT EXAMINATIONBY'
            match_3 = 'CROSS-EXAMINATION \(RESUMED\)BY'
            match_4 = 'DIRECT EXAMINATION \(RESUMED\)BY'
            #---------------------------------------------
            # Define all possible combinations (14)
            case = 0
            if df1['speech'].str.contains(match_1).any() and df1['speech'].str.contains(match_2).any() and df1['speech'].str.contains(match_3).any() and df1['speech'].str.contains(match_4).any(): 
                matching_points_1 = df1[df1["speech"].str.contains(match_1)]
                matching_indexes_1 = list(matching_points_1.index)
                matching_points_2 = df1[df1["speech"].str.contains(match_2)]
                matching_indexes_2 = list(matching_points_2.index)
                matching_points_3 = df1[df1["speech"].str.contains(match_3)]
                matching_indexes_3 = list(matching_points_3.index)
                matching_points_4 = df1[df1["speech"].str.contains(match_4)]
                matching_indexes_4 = list(matching_points_4.index) 
                matching_indexes_1.extend(matching_indexes_2+ matching_indexes_3 + matching_indexes_4)
                matching_indexes_1.sort() 
                matching_indexes_all = matching_indexes_1.copy()
                case = 1234
            elif df1['speech'].str.contains(match_2).any() and df1['speech'].str.contains(match_3).any() and df1['speech'].str.contains(match_4).any():
                matching_points_2 = df1[df1["speech"].str.contains(match_2)]
                matching_indexes_2 = list(matching_points_2.index)
                matching_points_3 = df1[df1["speech"].str.contains(match_3)]
                matching_indexes_3 = list(matching_points_3.index)
                matching_points_4 = df1[df1["speech"].str.contains(match_4)]
                matching_indexes_4 = list(matching_points_4.index)
                matching_indexes_2.extend(matching_indexes_3 + matching_indexes_4)
                matching_indexes_2.sort() 
                matching_indexes_all = matching_indexes_2.copy() 
                case = 234
            elif df1['speech'].str.contains(match_1).any() and df1['speech'].str.contains(match_3).any() and df1['speech'].str.contains(match_4).any(): 
                matching_points_1 = df1[df1["speech"].str.contains(match_1)]
                matching_indexes_1 = list(matching_points_1.index)
                matching_points_3 = df1[df1["speech"].str.contains(match_3)]
                matching_indexes_3 = list(matching_points_3.index)
                matching_points_4 = df1[df1["speech"].str.contains(match_4)]
                matching_indexes_4 = list(matching_points_4.index)
                matching_indexes_1.extend(matching_indexes_3 + matching_indexes_4)
                matching_indexes_1.sort() 
                matching_indexes_all = matching_indexes_1.copy()
                case = 134
            elif df1['speech'].str.contains(match_1).any() and df1['speech'].str.contains(match_2).any() and df1['speech'].str.contains(match_4).any(): 
                matching_points_1 = df1[df1["speech"].str.contains(match_1)]
                matching_indexes_1 = list(matching_points_1.index)
                matching_points_2 = df1[df1["speech"].str.contains(match_2)]
                matching_indexes_2 = list(matching_points_2.index)
                matching_points_4 = df1[df1["speech"].str.contains(match_4)]
                matching_indexes_4 = list(matching_points_4.index)
                matching_indexes_1.extend(matching_indexes_2 + matching_indexes_4)
                matching_indexes_1.sort() 
                matching_indexes_all = matching_indexes_1.copy()
                case = 124
            elif df1['speech'].str.contains(match_1).any() and df1['speech'].str.contains(match_2).any() and df1['speech'].str.contains(match_3).any(): 
                matching_points_1 = df1[df1["speech"].str.contains(match_1)]
                matching_indexes_1 = list(matching_points_1.index)
                matching_points_2 = df1[df1["speech"].str.contains(match_2)]
                matching_indexes_2 = list(matching_points_2.index)
                matching_points_3 = df1[df1["speech"].str.contains(match_3)]
                matching_indexes_3 = list(matching_points_3.index)
                matching_indexes_1.extend(matching_indexes_2+ matching_indexes_3)
                matching_indexes_1.sort() 
                matching_indexes_all = matching_indexes_1.copy()
                case = 123
            elif df1['speech'].str.contains(match_3).any() and df1['speech'].str.contains(match_4).any():
                matching_points_3 = df1[df1["speech"].str.contains(match_3)]
                matching_indexes_3 = list(matching_points_3.index)
                matching_points_4 = df1[df1["speech"].str.contains(match_4)]
                matching_indexes_4 = list(matching_points_4.index)
                matching_indexes_3.extend(matching_indexes_4)
                matching_indexes_3.sort() 
                matching_indexes_all = matching_indexes_3.copy() 
                case = 34
            elif df1['speech'].str.contains(match_2).any() and df1['speech'].str.contains(match_4).any():
                matching_points_2 = df1[df1["speech"].str.contains(match_2)]
                matching_indexes_2 = list(matching_points_2.index)
                matching_points_4 = df1[df1["speech"].str.contains(match_4)]
                matching_indexes_4 = list(matching_points_4.index)
                matching_indexes_2.extend(matching_indexes_4)
                matching_indexes_2.sort() 
                matching_indexes_all = matching_indexes_2.copy() 
                case = 24
            elif df1['speech'].str.contains(match_2).any() and df1['speech'].str.contains(match_3).any():
                matching_points_2 = df1[df1["speech"].str.contains(match_2)]
                matching_indexes_2 = list(matching_points_2.index)
                matching_points_3 = df1[df1["speech"].str.contains(match_3)]
                matching_indexes_3 = list(matching_points_3.index)
                matching_indexes_2.extend(matching_indexes_3)
                matching_indexes_2.sort() 
                matching_indexes_all = matching_indexes_2.copy()  
                case = 23
            elif df1['speech'].str.contains(match_1).any() and df1['speech'].str.contains(match_4).any():
                matching_points_1 = df1[df1["speech"].str.contains(match_1)]
                matching_indexes_1 = list(matching_points_1.index)
                matching_points_4 = df1[df1["speech"].str.contains(match_4)]
                matching_indexes_4 = list(matching_points_4.index)
                matching_indexes_1.extend(matching_indexes_4)
                matching_indexes_1.sort() 
                matching_indexes_all = matching_indexes_1.copy() 
                case = 14
            elif df1['speech'].str.contains(match_1).any() and df1['speech'].str.contains(match_3).any():
                matching_points_1 = df1[df1["speech"].str.contains(match_1)]
                matching_indexes_1 = list(matching_points_1.index)
                matching_points_3 = df1[df1["speech"].str.contains(match_3)]
                matching_indexes_3 = list(matching_points_3.index)
                matching_indexes_1.extend(matching_indexes_3)
                matching_indexes_1.sort() 
                matching_indexes_all = matching_indexes_1.copy() 
                case = 13
            elif df1['speech'].str.contains(match_1).any() and df1['speech'].str.contains(match_2).any():
                matching_points_1 = df1[df1["speech"].str.contains(match_1)]
                matching_indexes_1 = list(matching_points_1.index)
                matching_points_2 = df1[df1["speech"].str.contains(match_2)]
                matching_indexes_2 = list(matching_points_2.index)
                matching_indexes_1.extend(matching_indexes_2)
                matching_indexes_1.sort() 
                matching_indexes_all = matching_indexes_1.copy() 
                case = 12
            elif df1['speech'].str.contains(match_1).any():
                matching_points_1 = df1[df1["speech"].str.contains(match_1)]
                matching_indexes_1 = list(matching_points_1.index)
                matching_indexes_all = matching_indexes_1.copy()
                case = 1
            elif df1['speech'].str.contains(match_2).any():
                matching_points_2 = df1[df1["speech"].str.contains(match_2)]
                matching_indexes_2 = list(matching_points_2.index)
                matching_indexes_all = matching_indexes_2.copy() 
                case = 2
            elif df1['speech'].str.contains(match_3).any():
                matching_points_3 = df1[df1["speech"].str.contains(match_3)]
                matching_indexes_3 = list(matching_points_3.index)
                matching_indexes_all = matching_indexes_3.copy()
                case = 3
            elif df1['speech'].str.contains(match_4).any():
                matching_points_4 = df1[df1["speech"].str.contains(match_4)]
                matching_indexes_4 = list(matching_points_4.index)
                matching_indexes_all = matching_indexes_4.copy() 
                case = 4

            # If we have at least one match, substitute 'Q: ' with the name of the attorney
            if case != 0:
                questioners = list()
                for i in range(0, len(matching_indexes_all)):
                    Q_name = df1.iloc[matching_indexes_all[i], 1].split("BY ")[1]
                    questioners.append(Q_name)
                    if i < (len(matching_indexes_all)-1):
                        for row in range(matching_indexes_all[i], matching_indexes_all[i + 1]):
                            if df1.iloc[row, 0] == '#Q: ':
                                df1.iloc[row, df1.columns.get_loc('person')] = Q_name
                    else:
                        for row in range(matching_indexes_all[i], nrow):
                            if df1.iloc[row, 0] == '#Q: ':
                                df1.iloc[row, df1.columns.get_loc('person')] = Q_name
            
            # Append the df of each file under the previous one
            df = df.append(df1, ignore_index = True)
    return df