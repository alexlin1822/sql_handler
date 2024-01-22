# import sys
# from sys import common
import re
import common as common


TITLE_TABLE = 'CREATE TABLE'.lower()
TITLE_VIEW = 'create or replace view'.lower()
TITLE_M_VIEW = 'create materialized view'.lower()
TITLE_PROCEDURE = 'CREATE PROCEDURE'.lower()
TITLE_FUNCTION = 'CREATE OR REPLACE FUNCTION'.lower()


def copy_file_lines(input_file, output_file):
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                outfile.write(line)
    except IOError as e:
        raise IOError(f"Error copying file: {e}")


def replace_to_char(text):
    TC = "to_char"
    new_line = text.lower()
    results = get_to_char_string(new_line)

    for result in results:
        new_line = new_line.replace(result, result[len(TC):]+"::varchar")

    # try:
    #     matches = re.findall(r"to_char \(([^,]+)\)", new_line)
    #     for match in matches:
    #         if "," not in match:
    #             # new_line = re.sub(rf"to_char \({match}\)", rf"({match})::varchar", new_line)
    #             rest_str = re.sub(rf"to_char \({match}\)", rf"({match})::varchar", new_line)
    # except :
    #     rest_str=new_line

    # try:
    #     matches = re.findall(r"to_char\(([^,]+)\)", new_line)
    #     for match in matches:
    #         if "," not in match:
    #             rest_str = re.sub(rf"to_char\({match}\)", rf"({match})::varchar", new_line)
    # except :
    #     rest_str=new_line
    return new_line

# recuive to find string


def get_to_char_string(input_str):
    results = []
    rest_str = input_str
    TC = "to_char"

    while (rest_str.strip() != ""):
        block_end_index = -1
        tochar_index = rest_str.find(TC+"(")

        if tochar_index < 0:
            tochar_index = rest_str.find(TC+" (")

        if tochar_index > -1:
            rest_str = rest_str[tochar_index:]

            i = 0
            has_comma = False

            for j, char in enumerate(rest_str):
                if i == 1 and char == ',':
                    has_comma = True
                if char == '(':
                    i += 1
                if char == ')':
                    i -= 1
                    block_end_index = j+1

                    if i == 0:
                        if has_comma == False:
                            new_block = rest_str[:block_end_index]
                            results.append(new_block)

                            new_tochar_index = new_block.find(TC+"(")

                            if new_tochar_index < 0:
                                new_tochar_index = new_block.find(TC+" (")

                            if new_tochar_index > -1:
                                sub_results = get_to_char_string(
                                    new_block[len(TC):])
                                for sub_result in sub_results:
                                    results.append(sub_result)

                        rest_str = rest_str[block_end_index+1:]
                        break

        if block_end_index == -1:
            break
    return results

# MView grammar Fixing


def mview_fix(input_file, output_file):
    # source file need fix or not
    needFixing = True
    isBlock = False
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                new_line = line.lower()

                if needFixing:
                    ### change Title from view to mview ###
                    if TITLE_VIEW.lower() in new_line.lower():
                        # if "_mv" in line.lower():
                        new_line = new_line.lower().replace(TITLE_VIEW+" ", TITLE_M_VIEW+" ")

                    if TITLE_M_VIEW in new_line:
                        new_line = new_line.replace('"', '')
                        match = re.search(r"(.*?)\(", new_line)
                        if match:
                            new_line = match.group(1)+" AS\n"

                    # ### Delete [12034] note ###
                    # if new_line.strip() == "\n" :
                    #     new_line == ""
                    if new_line == "/*\n":
                        new_line = ""
                    if new_line.strip().startswith('[') and new_line.strip().endswith(']'):
                        new_line = ""
                    if new_line.strip() == "*/;":
                        new_line = ";\n\n"

                    ### to_char ###
                    # new_line=replace_str("aws_oracle_ext.to_char","to_char",new_line)
                    msg = "aws_oracle_ext.to_char"
                    if msg in new_line:
                        new_line = new_line.replace(msg, 'to_char')

                    # new_line=replace_str("varchar2","varchar",new_line)
                    msg = "varchar2"
                    if msg in new_line:
                        new_line = new_line.replace(msg, 'varchar')

                    # new_line=replace_str("substr (","substring (",new_line)
                    msg = "substr ("
                    if msg in new_line:
                        new_line = new_line.replace(msg, "substring (")

                    # new_line=replace_str("substr(","substring (",new_line)
                    msg = "substr("
                    if msg in new_line:
                        new_line = new_line.replace(msg, "substring (")

                    ### To_char  ###
                    new_line = replace_to_char(new_line)

                    ### To_NUMBER  ###
                    # if "aws_oracle_ext.To_NUMBER" in line:
                    #     new_line = new_line.replace('aws_oracle_ext.To_NUMBER','To_NUMBER')

                    # try:
                    #     matches = re.findall(r"TO_NUMBER \(([^,]+)\)", new_line)
                    #     # print(matches)
                    #     for match in matches:
                    #         if "," not in match:
                    #             new_line = re.sub(rf"TO_NUMBER \({match}\)", rf"({match})::numeric", new_line)

                    #     matches = re.findall(r"To_NUMBER\(([^,]+)\)", new_line)
                    #     # print(matches)
                    #     for match in matches:
                    #         if "," not in match:
                    #             new_line = re.sub(rf"To_NUMBER\({match}\)", rf"({match})::numeric", new_line)
                    # except :
                    #     print("Line Error (to_char):    "+ new_line)

                    # ###  from DUAL  ###
                    if " from DUAL" in new_line:
                        new_line = new_line.replace(' from DUAL', '')

                    ### TimeStamp_PARSE  ###
                    if "aws_oracle_ext.TO_TIMESTAMP_PARSE" in new_line:
                        new_line = new_line.replace(
                            'aws_oracle_ext.TO_TIMESTAMP_PARSE', 'TO_DATE')
                        new_line = new_line.replace(", 'AMERICAN'", "")

                    if "aws_oracle_ext.TO_TIMESTAMP" in new_line:
                        new_line = new_line.replace(
                            'aws_oracle_ext.TO_TIMESTAMP', 'TO_DATE')
                        new_line = new_line.replace(", 'AMERICAN'", "")

                    # new rules here..........
                    # msg="(trunc (sysdate, 'mm'), 'month')::varchar"
                    # if msg in new_line:
                    #     new_line = new_line.replace(msg,"TO_CHAR(sysdate, 'Month')")

                    # msg="to_char (initcap (r2.preferred_first_nm || ' ' || r2.last_nm)"
                    # if msg in new_line:
                    #     new_line = new_line.replace(msg,"(initcap (r2.preferred_first_nm || ' ' || r2.last_nm)::varchar")

                    # # combine block
                    # if "then" in new_line:
                    #     isBlock=False

                    # if isBlock:
                    #     new_line=new_line[:-1].strip()

                    # if "least " in new_line:
                    #     isBlock=True
                    #     new_line=new_line[:-1].strip()

                    ######### output##############
                    # if new_line.strip()!="":
                outfile.write(new_line)
    except IOError as e:
        raise IOError(f"Error copying file: {e}")

    add_schema_generate_index(schema_name, output_file_fix_mv,
                              output_file_dp, output_index_org, TITLE_M_VIEW, needFixing)
    make_order(output_index_org, output_index_final)
    create_new_file_by_order(
        output_index_final, output_file_dp, output_final_mv, TITLE_M_VIEW)

# View grammar Fixing


def view_fix(input_file, output_file):
    # source file need fix or not
    needFixing = True
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            i = 0
            for line in infile:
                new_line = line.lower()
                if needFixing:
                    # output index file ###  add_schema_generate_index replace this function
                    # if TITLE_VIEW in new_line.lower():
                    #     # if "_vw" in line.lower():
                    #     i+=1
                    #     match = re.search(TITLE_VIEW+ r" (.*?)\(", new_line.lower())

                    #     if match:
                    #         substring = match.group(1)  # Access the captured group
                    #         print(substring)
                    #         # indexfile.write(str(i)+","+substring+"\n")
                    #     else:
                    #         print("No "+TITLE_VIEW+" found")

                    # Add ID to each create view
                    # new_line = line.lower().replace("create or replace view ", "--"+str(i)+"\ncreate or replace view ")

                    ### Delete 12034 ###
                    # new_line=replace_str("' AS text,'","",new_line)
                    msg = "' AS text,'".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "")

                    # new_line=replace_str("12034 - severity critical - amazon redshift doesn\\'t support the to_char function with a number of arguments. perform a manual conversion.","",new_line)
                    msg = "12034 - severity critical - amazon redshift doesn\\'t support the to_char function with a number of arguments. perform a manual conversion.".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "")

                    # new_line=replace_str("12034 - Severity CRITICAL - Amazon Redshift doesn't support the to_char function with a number of arguments. Perform a manual conversion.","",new_line)
                    msg = "12034 - Severity CRITICAL - Amazon Redshift doesn't support the to_char function with a number of arguments. Perform a manual conversion.".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "")

                    # new_line=replace_str("12034 - severity critical - amazon redshift doesn't support the count(<dynamic_type>) function with a number of arguments. perform a manual conversion.","",new_line)
                    msg = "12034 - severity critical - amazon redshift doesn't support the count(<dynamic_type>) function with a number of arguments. perform a manual conversion.".lower(
                    )
                    if msg in new_line:
                        new_line = new_line.replace(msg, "")

                    # new_line=replace_str("9996 - severity critical - transformer error occurred in plsqlstatement. please submit report to developers.","",new_line)
                    msg = "9996 - severity critical - transformer error occurred in plsqlstatement. please submit report to developers."
                    if msg in new_line:
                        new_line = new_line.replace(msg, "")

                    # new_line=replace_str("\\'","'",new_line)
                    msg = "\\'".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "'")

                    # new_line=replace_str("' AS error_msg;","",new_line)
                    msg = "' AS error_msg;".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "")

                    # new_line=replace_str("select 'create or replace force view","create or replace view",new_line)
                    msg = "select 'create or replace force view".lower()
                    if msg in new_line:
                        new_line = new_line.replace(
                            msg, "create or replace view")

                    ### to_char ###
                    # if "aws_oracle_ext.to_char" in new_line:
                    #     new_line = new_line.replace('aws_oracle_ext.to_char','to_char')

                    try:
                        matches = re.findall(r"to_char \(([^,]+)\)", new_line)
                        # print(matches)
                        for match in matches:
                            if "," not in match:
                                # new_line = re.sub(rf"to_char \({match}\)", rf"({match})::varchar", new_line)
                                new_line = re.sub(
                                    rf"to_char \({match}\)", rf"({match})::varchar", new_line)

                        # print(matches)
                        matches = re.findall(r"to_char\(([^,]+)\)", new_line)
                        for match in matches:
                            if "," not in match:
                                new_line = re.sub(
                                    rf"to_char\({match}\)", rf"({match})::varchar", new_line)
                    except:
                        print("Line Error (to_char):    " + new_line)

                    # ## To_NUMBER  ###
                    # if "aws_oracle_ext.To_NUMBER" in line:
                    #     new_line = new_line.replace('aws_oracle_ext.To_NUMBER','To_NUMBER')

                    # try:
                    #     matches = re.findall(r"TO_NUMBER \(([^,]+)\)", new_line)
                    #     # print(matches)
                    #     for match in matches:
                    #         if "," not in match:
                    #             new_line = re.sub(rf"TO_NUMBER \({match}\)", rf"({match})::numeric", new_line)

                    #     matches = re.findall(r"To_NUMBER\(([^,]+)\)", new_line)
                    #     # print(matches)
                    #     for match in matches:
                    #         if "," not in match:
                    #             new_line = re.sub(rf"To_NUMBER\({match}\)", rf"({match})::numeric", new_line)
                    # except :
                    #     print("Line Error (to_char):    "+ new_line)

                    ###  from DUAL  ###
                    if " from DUAL" in new_line:
                        new_line = new_line.replace(' from DUAL', '')

                    ### TimeStamp_PARSE  ###
                    if "aws_oracle_ext.TO_TIMESTAMP_PARSE" in new_line:
                        new_line = new_line.replace(
                            'aws_oracle_ext.TO_TIMESTAMP_PARSE', 'TO_DATE')
                        new_line = new_line.replace(", 'AMERICAN'", "")

                    if "aws_oracle_ext.TO_TIMESTAMP" in new_line:
                        new_line = new_line.replace(
                            'aws_oracle_ext.TO_TIMESTAMP', 'TO_DATE')
                        new_line = new_line.replace(", 'AMERICAN'", "")

                    # new rules here..........

                    ######### output##############
                if "(text, error_msg)" not in new_line:
                    outfile.write(new_line)
    except IOError as e:
        raise IOError(f"Error copying file: {e}")

    add_schema_generate_index(schema_name, output_file_fix_vw,
                              output_file_dp, output_index_org, TITLE_VIEW, needFixing)
    make_order(output_index_org, output_index_final)
    create_new_file_by_order(
        output_index_final, output_file_dp, output_final_vw, TITLE_VIEW)


def Function_fix(input_file, output_file):
    # source file need fix or not
    needFixing = True
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                new_line = line.lower()

                if needFixing:
                    # ### Delete [12054] note ###
                    msg = "#/*".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "")

                    # msg="#[12054 - Severity CRITICAL - Amazon Redshift doesn't support the FROM statement inside of PL/pgSQL block. Perform a manual conversion.]".lower()
                    # if msg in new_line:
                    #     new_line = new_line.replace(msg,"")

                    msg = "[12054 - severity critical ".lower()
                    if msg in new_line:
                        new_line = ""

                    msg = "#*/".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "")

                    msg = "substr(".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "substring (")

                    msg = "substr (".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "substring (")

                    msg = "#".lower()
                    if new_line.startswith(msg):
                        new_line = new_line[1:]

                    if "language plpythonu;" in new_line:
                        new_line += "\n"

                    # new rules here..........

                ######### output##############
                if new_line.strip() != "":
                    outfile.write(new_line)
    except IOError as e:
        raise IOError(f"Error copying file: {e}")

    add_schema_generate_index(schema_name, output_file_fix_fu,
                              output_final_fu, output_index_final, TITLE_FUNCTION, False)


def procedure_fix(input_file, output_file):
    # source file need fix or not
    needFixing = False
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                new_line = line.lower()

                if needFixing:
                    # ### Delete [12054] note ###

                    if "/*".lower() in new_line and "*/".lower() not in new_line:
                        msg = "/*".lower()
                        new_line = new_line.replace(msg, "")

                    if "/*".lower() not in new_line and "*/".lower() in new_line:
                        msg = "*/".lower()
                        new_line = new_line.replace(msg, "")

                    msg = "- Severity CRITICAL - ".lower()
                    if msg in new_line:
                        new_line = ""

                    msg = ":=".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "=")

                    msg = "substr(".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "substring (")

                    msg = "substr (".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "substring (")

                    msg = "substr (".lower()
                    if msg in new_line:
                        new_line = new_line.replace(msg, "substring (")

                    msg = r"dbms_mview\.refresh\s*\(\s*'([^']*)'\s*\)"
                    new_line = re.sub(
                        msg, r"REFRESH MATERIALIZED VIEW \1;", new_line)

                    msg = r"dbms_mview\.refresh\s*\(\s*'(.+?)'\s*,\s*'c'\s*\)"
                    new_line = re.sub(
                        msg, r"REFRESH MATERIALIZED VIEW \1;", new_line)

                    msg = r"dbms_mview\.refresh\s*\(\s*'(.+?)'\s*,\s*atomic_refresh=>false\s*\)"
                    new_line = re.sub(
                        msg, r"REFRESH MATERIALIZED VIEW \1;", new_line)

                    new_line = new_line.lower()
                    # msg="#".lower()
                    # if new_line.startswith(msg):
                    #     new_line = new_line[1:]

                    if "language plpythonu;" in new_line:
                        new_line += "\n"

                    # new rules here..........

                ######### output##############
                if new_line.strip() != "":
                    outfile.write(new_line)
    except IOError as e:
        raise IOError(f"Error copying file: {e}")

    add_schema_generate_index(schema_name, output_file_fix_pr,
                              output_final_pr, output_index_final, TITLE_PROCEDURE, False)


def generate_index(input_file, output_index_file, db_object_type):
    try:
        with open(input_file, 'r') as infile, open(output_index_file, 'w') as indexfile:
            i = 0
            index_string = ""

            for line in infile:
                new_line = line
                # output_line=line

                # handle each schema block #
                if new_line.strip().lower().startswith(db_object_type):
                    if index_string != "":
                        indexfile.write(index_string+"\n")
                        index_string = ""

                    i += 1
                    # Getting object name
                    object_title = get_object_name(new_line.lower())
                    if object_title != "":
                        # index_string+=str(i)+","+object_title.strip().lower()+","
                        index_string += object_title.strip().lower()
                    else:
                        print("No object_title found:  "+line.lower())

                ### Add schema name for table  ###
                # outfile.write(output_line)

            if index_string != "":
                indexfile.write(index_string)
            print(i)

    except IOError as e:
        raise IOError(f"Error copying file: {e}")

# add schema_name and generate index file


def add_schema_generate_index(schema_name, input_file, output_file, output_org_index_file, db_object_type, needFixing):
    # source file need fix or not  (Add schema_name for table)
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile, open(output_org_index_file, 'w') as indexfile:
            i = 0
            getting = False
            comment_block = False
            index_string = ""

            for line in infile:
                new_line = line
                output_line = line

                if needFixing:
                    # skip /* */ comments  ###  has problem need check
                    pattern = r"/\*.*?\*/"  # Regular expression to match comments
                    new_line = re.sub(pattern, "", new_line, flags=re.DOTALL)

                    right_index = new_line.find("/*")

                    if right_index > -1:
                        # new_line=new_line[:right_index-len("/*")]
                        new_line = new_line[:right_index]
                        # print("/*  :  "+new_line)
                        comment_block = True

                    if comment_block:
                        left_index = new_line.find("*/")

                        if left_index > -1:
                            new_line = new_line[left_index+len("/*"):]
                            comment_block = False
                        else:
                            outfile.write(output_line)
                            continue

                    ### skip -- comments  ###
                    right_index = new_line.find("--")

                    if right_index > -1:
                        new_line = new_line[:right_index]

                # handle each schema block #
                # print("Title here: "+title)
                if db_object_type in new_line.lower():
                    if index_string != "":
                        indexfile.write(index_string+"\n")
                        index_string = ""

                    i += 1
                    # Getting object name
                    object_title = get_object_name(new_line.lower())
                    if object_title != "":
                        index_string += str(i)+"," + \
                            object_title.strip().lower()+","
                    else:
                        print("No object_title found:  "+new_line.lower())

                    # match = re.search(db_object_type+ r" (.*?)\(", new_line.lower())

                    # if match:
                    #     substring = match.group(1)  # Access the captured group
                    #     index_string+=str(i)+","+substring.strip().lower()+","
                    # else:
                    #     print("No substring found")

                ### Getting table ###
                # Handling FROM block
                if "FROM " in new_line.upper() and not "FROM (" in new_line.upper():
                    if not "/* FROM" in new_line.upper() and not "/*FROM" in new_line.upper():
                        getting = True
                        detail = new_line.upper().strip()
                        start_index = detail.find("FROM ")
                        start_index += len("FROM ")
                        new_line = detail[start_index:]

                if getting:
                    detail = new_line.upper().strip()
                    start_index = 0
                    end_index = -1
                    # print(detail)
                    if end_index == -1 and getting:
                        end_index = detail.find("WHERE", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find("GROUP BY", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find("LEFT ", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find("RIGHT ", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find("INNER ", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find("OUTER ", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find("JOIN ", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find("CONNECT BY ", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find("UNION", start_index)
                        if end_index > -1:
                            getting = False

                    if end_index == -1 and getting:
                        end_index = detail.find(";", start_index)
                        if end_index > -1:
                            getting = False

                    # Add more end keyword here....

                    #####

                    if end_index == -1:
                        end_index = len(detail)

                    results = detail[start_index:end_index]
                    results = results.strip().lower()

                    for each_result in results.split(','):
                        each_value = each_result.strip()
                        if each_value != "":
                            result = each_value.split(" ")[0]
                            if result[-1:] == ';':
                                result = result[:-1]
                                getting = False
                            if result[-1:] == ')':
                                result = result[:-1]
                                getting = False
                            if result[-1:] == ',':
                                result = result[:-1]

                            if result.startswith('/*'):
                                result = ""
                            if result.startswith('('):
                                result = ""

                            # if result!="":
                            if result != "" and not "'" in result and not "*/" in result and not "/*" in result and not "(" in result and not ")" in result:
                                if not "." in result:
                                    if needFixing:
                                        output_line = output_line.replace(
                                            result, schema_name+"."+result)
                                        result = schema_name+"."+result

                                if not result+"," in index_string:
                                    index_string += result+","

                                # print("Table: "+ result)

                # Handling JOIN block
                if "JOIN " in new_line.upper() and not "JOIN (" in new_line.upper():
                    # print("JOIN:    "+ new_line)
                    detail = new_line.upper().strip()
                    start_index = detail.find("JOIN ")
                    start_index += len("JOIN ")
                    temp_str = detail[start_index:].strip()
                    # print("JOIN clear:    "+ temp_str)
                    if temp_str != "":
                        detail_list = temp_str.split(" ")
                        table_name = detail_list[0]
                        if not "." in table_name:
                            if needFixing:
                                result = schema_name+"."+table_name
                            else:
                                result = table_name
                            msg = table_name.lower()
                            if msg in output_line:
                                output_line = output_line.lower().replace(msg, result)
                            index_string += result+","

                ### Add schema name for table  ###
                outfile.write(output_line)

            if index_string != "":
                indexfile.write(index_string)

    except IOError as e:
        raise IOError(f"Error copying file: {e}")


def make_order(input_index_file, output_index_file):
    try:
        with open(input_index_file, 'r') as infile, open(output_index_file, 'w') as outfile:
            list_table = []
            list_line = []

            for line in infile:
                list_line.append(line)
                detail = line.split(',')
                list_table.append(detail[1])
            # print(line)
            i = 0
            while (i < len(list_line)):
                detail = list_line[i].split(',')
                for value in detail[2:]:
                    if value.strip() != '':
                        # print(value)
                        index = -1
                        try:
                            index = list_table.index(value)
                        except ValueError:
                            index = -1

                        if index > i:
                            temp = list_line[i]
                            list_line[i] = list_line[index]
                            list_line[index] = temp

                            temp = list_table[i]
                            list_table[i] = list_table[index]
                            list_table[index] = temp

                            continue
                i += 1

            for output_line in list_line:
                outfile.write(output_line)

    except IOError as e:
        raise IOError(f"Error copying file: {e}")


def create_new_file_by_order(index_file, input_file, output_file, title):
    try:
        list_table = []
        list_line = []

        with open(index_file, 'r') as infile:
            for line in infile:
                detail = line.split(',')
                list_table.append(detail[1])

        with open(input_file, 'r') as infile:
            for line in infile:
                list_line.append(line)

        with open(output_file, 'w') as outfile:
            for table in list_table:
                table = table.lower()

                start_id = -1
                getting = False

                for text in list_line:
                    text = text.lower()

                    if getting:
                        outfile.write(text)
                        if ';' in text:
                            getting = False
                            outfile.write("\n")
                            break

                    else:
                        if text.startswith(title+' '+table):
                            getting = True
                            outfile.write(text)

    except IOError as e:
        raise IOError(f"Error copying file: {e}")


def add_comments(input_file, output_file, index_file, schema_name):
    schema_name = schema_name.lower()
    try:
        list_comments = []
        with open(index_file, 'r') as comments:
            for comment in comments:
                list_comments.append(comment)

        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            i = 0

            for line in infile:
                line = line.lower()
                if line.startswith("create ") and schema_name in line:
                    title = get_object_name(line)

                    if title != "":
                        # first element in comment must be object(view or mivew) name
                        for comment in list_comments:
                            detail = comment.split(",")
                            # print("comment:  "+comment)
                            # print("detail[0]: "+ detail[0].strip().lower())
                            if title.lower() == detail[0].strip().lower():
                                # line="-- "+str(i)+"  "+detail[1]+"   "+detail[2]+"   "+detail[3]+line
                                # line="-- "+"  "+detail[1]+"   "+detail[2]+"   "+detail[3]+line
                                line = "-- "+"  " + \
                                    detail[1]+"   "+detail[2]+"\n"+line
                                break

                    # title=line
                    # start_index = title.find(schema_name)
                    # if start_index >-1:
                    #     i+=1
                    #     title=title[start_index:]
                    #     start_index = title.find("(")
                    #     if start_index>-1:
                    #         title=title[:start_index]
                    #     else:
                    #         temp=title.split(" ")
                    #         title=temp[0]
                    #     title=title.strip()
                    #     print("title: "+ title)

                    #     comment_string=""

                    #     #first element in comment must be object(view or mivew) name
                    #     for comment in list_comments:
                    #         detail=comment.split(",")
                    #         # print("comment:  "+comment)
                    #         # print("detail[0]: "+ detail[0].strip().lower())
                    #         if title.lower()==detail[0].strip().lower():
                    #             # line="-- "+str(i)+"  "+detail[1]+"   "+detail[2]+"   "+detail[3]+line
                    #             line="-- "+"  "+detail[1]+"   "+detail[2]+"   "+detail[3]+line
                    #             break

                outfile.write(line)
    except IOError as e:
        raise IOError(f"Error copying file: {e}")


# TODO: Donot work
# def replace_str(str_input,str_replace,new_line):
#     new_line=new_line.lower()
#     str_input=str_input.lower()
#     str_replace=str_replace.lower()

#     if str_input in new_line:
#         return new_line.replace(str_input,str_replace)


# get the tree for mview and view


def get_tree():
    error_object_list = "D:\\MyProgram\\Python\\sql_handler\\A\\A\\source\\error_object_list.txt"
    output_error_object_list = "D:\\MyProgram\\Python\\sql_handler\\A\\A\\final\\output_error_object_list.txt"
    index_list = []

    add_schema_generate_index(
        schema_name, source_mv, output_file_dp, output_index_org, TITLE_M_VIEW, False)
    with open(output_index_org, 'r') as infile:
        for line in infile:
            line = line.lower()
            index_list.append(line)

    add_schema_generate_index(
        schema_name, source_vw, output_file_dp, output_index_org, TITLE_VIEW, False)
    with open(output_index_org, 'r') as infile:
        for line in infile:
            line = line.lower()
            index_list.append(line)

    whole_resuls = []
    with open(error_object_list, 'r') as infile:
        whole_resuls.append("Base missing objects:")
        for error_object in infile:
            error_object = error_object.lower().strip()
            whole_resuls.append(error_object)
    whole_resuls.append("\n")

    with open(error_object_list, 'r') as infile, open(output_error_object_list, 'w') as outfile:
        for error_object in infile:
            error_object = error_object.lower().strip()
            whole_resuls.append("-- relation "+error_object)

            new_results = rec_get_child(index_list, error_object, "")
            for line in new_results:
                whole_resuls.append("    "+line)
            whole_resuls.append("\n")

        for final_result in whole_resuls:
            print(final_result)
            outfile.write(final_result+"\n")


def rec_get_child(index_list, error_object, indient_str):
    results = []
    indient_str += "    "
    if "--" in error_object:
        return results
    for line in index_list:
        if error_object+"," in line:
            object_list = line.split(",")
            object = object_list[1].lower().strip()
            if error_object != object:
                results.append(object)
                new_results = rec_get_child(index_list, object, indient_str)

                for new_result in new_results:
                    results.append(indient_str+new_result)
        # elif (error_object=="dm_admin.") and error_object in line:
        #     object_list=line.split(",")
        #     object=object_list[1].lower().strip()

        #     if error_object not in object:
        #         results.append(object)
        #         new_results=rec_get_child(index_list,object,indient_str)

        #         for new_result in new_results:
        #             results.append(indient_str+new_result)

    return results


def add_something():
    input_file = source_pr
    output_file = output_final_pr

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        need_add_commit = False

        for line in infile:
            outfile.write(line)
            if "execute 'delete from " in line:
                need_add_commit = True
            if need_add_commit and ";" in line:
                need_add_commit = False
                outfile.write("commit;\n")


def getObjectList_oracle():
    # title="CREATE MATERIALIZED VIEW ".upper()
    title = "create or replace force view".upper()
    input_file = "D:\\MyProgram\\Python\\sql_handler\\A\\Original\\us_comm_ops_oracle.sql"
    output_file = "D:\\MyProgram\\Python\\sql_handler\\A\\final\\index_list.txt"

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            if line.upper().startswith(title):
                temp = line[len(title):].strip()

                # view end
                block_end_index = -1
                tochar_index = temp.find("(")

                if tochar_index > -1:
                    temp = temp[:tochar_index]

                temp = temp.replace('"', '')
                outfile.write(temp+"\n")


def getObjectList_redshift():

    input_file = "D:\\MyProgram\\Python\\sql_handler\\A\\A\\final\\us_comm_ops_source.txt"
    output_file = "D:\\MyProgram\\Python\\sql_handler\\A\\final\\index_list.txt"

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Table list
            # title="CREATE TABLE ".upper()
            # if line.upper().startswith('--'+title):
            #     temp=line[len('--'+title):-2].strip()
            #     temp=temp.replace('"','')
            #     outfile.write(temp+"\n")
            # elif line.upper().startswith(title):
            #     if line[-3:].upper()==" AS":
            #         temp=line[len(title):-4].strip()
            #     else:
            #         temp=line[len(title):-2].strip()
            #     outfile.write(temp+"\n")

            # view list
            title = "CREATE OR REPLACE VIEW ".upper()
            if line.upper().startswith('--'+title):
                temp = line[len('--'+title):-2].strip()

                temp = temp.replace('"', '')
                tochar_index = temp.find("(")

                if tochar_index > -1:
                    temp = temp[:tochar_index]

                temp = temp.replace('"', '')
                outfile.write(temp+"\n")

            elif line.upper().startswith(title):
                temp = line[len(title):-2].strip()

                temp = temp.replace('"', '')
                tochar_index = temp.find("(")

                if tochar_index > -1:
                    temp = temp[:tochar_index]

                temp = temp.replace('"', '')
                outfile.write(temp+"\n")

            # Mview List
            # title="CREATE MATERIALIZED VIEW ".upper()
            # if line.upper().startswith('--'+title):
            #     temp=line[len('--'+title):].strip()
            #     temp=temp.replace(" AS","")
            #     temp=temp.replace(" as","")
            #     temp=temp.replace('"','')
            #     outfile.write(temp+"\n")
            # elif line.upper().startswith(title):
            # # if line.upper().startswith(title):
            #     # print(line[-3:].upper())
            #     # if line[-3:].upper()==" AS":
            #     #     temp=line[len(title):-4].strip()
            #     # else:
            #     temp=line[len(title):].strip()
            #     temp=temp.replace(" AS","")
            #     temp=temp.replace(" as","")
            #     temp=temp.replace('"','')
            #     outfile.write(temp+"\n")


def list_all_pr_dependent_objects():
    input_file = source_pr
    output_index_file = output_index_final
    try:
        with open(input_file, 'r') as infile, open(output_index_file, 'w') as outfile:
            procedure_name = ""
            index_str = ""
            # loading = False
            getting = False
            resuls = []
            sql_str = ""
            for line in infile:
                line = line.lower()
                a1 = line.find('--')
                if a1 > -1:
                    line = line[:a1]

                # Procedures
                if line.lower().startswith(TITLE_PROCEDURE.lower()):
                    procedure_name = line[len(TITLE_PROCEDURE):]
                    end_keyword = '('
                    end_index = procedure_name.find(end_keyword)
                    if end_index > -1:
                        procedure_name = procedure_name[:end_index].strip()

                insert_into_name = common.get_insert_into_object_name(line)
                # print("Insert into name: "+insert_into_name)

                if insert_into_name != "":
                    inst = line.lower().find("insert into ")
                    inst_str = line.lower()[inst+len("insert into "):]
                    sql_str = line.lower()[inst:].strip()
                    getting = True

                    if sql_str[-1:] == '\n':
                        sql_str = sql_str[:-1]+" "
                    else:
                        sql_str += ' '
                    # if index_str != "":
                    #     outfile.write(index_str)
                    index_str = '\n['+procedure_name+'],' + inst_str+','
                    loading = True
                elif getting:
                    inst = line.lower().find(";")
                    if inst > -1:
                        sql_str += line[:inst]
                        getting = False
                        sql_str = sql_str.replace('\t', '')
                        sql_str = sql_str.replace('\r', '')
                        sql_str = re.sub(r"\s+from\s+\(", " from(", sql_str)
                        sql_str = re.sub(r"\s+join\s+\(", " join(", sql_str)
                        sql_str = re.sub(r"/\*.*?\*/", "", sql_str)

                        temp = []
                        temp.append(procedure_name)
                        temp.append(sql_str)
                        resuls.append(temp)
                        print("sql: "+sql_str)
                        # print("get_table_from_insert_into: " +
                        #       common.get_table_from_insert_into(sql_str))
                        # print(sql_str)
                    else:
                        if line[-1:] == '\n':
                            sql_str += line[:-1].strip()+" "
                        else:
                            sql_str += line.strip()+" "

            # for result in resuls:
            #     print(result)

            if index_str != "":
                outfile.write(index_str+'\n')
    except IOError as e:
        raise IOError(f"Error copying file: {e}")


def one_test_funcion():
    """one object testing"""
    # spile_object(input_file,object_type,schema_name):
    results = common.split_object(source_pr, TITLE_PROCEDURE, schema_name)
    # print(results)

    results = common.split_statement_using_semiqute_for_one_object(
        results[0][2])

    temp_results = []
    print(results[5])
    print("=====================================")

    results = common.get_table_in_one_sql_statement_rec(
        results[5], temp_results)

    # output to file
    try:
        output_index_file = output_final_pr
        with open(output_index_file, 'w') as outfile:
            outfile.write("result 5 \n")
            for result in results:
                # outfile.write(result[2]+"\n\n")
                outfile.write(result+"\n")
    except IOError as e:
        raise IOError(f"Error copying file: {e}")


def all_result_test_funcion():
    """one object testing"""
    # spile_object(input_file,object_type,schema_name):
    output_str = ""
    results = []
    for result_split_object in common.split_object(source_pr, TITLE_PROCEDURE, schema_name):
        for result_one_statement in common.split_statement_using_semiqute_for_one_object(result_split_object[2]):
            # results.append(result_one_statement)
            output_str = result_split_object[0]+"," + \
                common.get_insert_into_object_name(result_one_statement)+","
            print(result_one_statement)
            temp_results = []
            for table_names in common.get_table_in_one_sql_statement_rec(result_one_statement, temp_results):
                output_str += table_names+","
                temp_results = []

            # output_str += "\n"
            # print(output_str)
            results.append(output_str)

    # output to file
    try:
        output_index_file = output_final_pr
        with open(output_index_file, 'w') as outfile:
            for result in results:
                outfile.write(result+"\n")
    except IOError as e:
        raise IOError(f"Error copying file: {e}")


if __name__ == "__main__":
    # change schema name here
    schema_name = "new_schemas"

    # #Source

    # Source
    source_mv = "D:\\MyProgram\\Python\\sql_handler\\a\\source_mv.txt"
    source_vw = "D:\\MyProgram\\Python\\sql_handler\\a\\source_vw.txt"
    source_fu = "D:\\MyProgram\\Python\\sql_handler\\a\\source_fu.txt"
    source_pr = "D:\\MyProgram\\Python\\sql_handler\\a\\source_pr.txt"

    # Process
    output_file_fix_mv = "D:\\MyProgram\\Python\\sql_handler\\a\\process\\output_fix_mv.txt"
    output_file_fix_vw = "D:\\MyProgram\\Python\\sql_handler\\a\\process\\output_fix_vw.txt"
    output_file_fix_fu = "D:\\MyProgram\\Python\\sql_handler\\a\\process\\output_fix_fu.txt"
    output_file_fix_pr = "D:\\MyProgram\\Python\\sql_handler\\a\\process\\output_fix_pr.txt"
    output_file_dp = "D:\\MyProgram\\Python\\sql_handler\\a\\process\\output_fix_dp.txt"
    output_index_org = "D:\\MyProgram\\Python\\sql_handler\\a\\process\\index_org.txt"

    # output
    output_index_final = "D:\\MyProgram\\Python\\sql_handler\\a\\final\\index_final.txt"
    output_final_mv = "D:\\MyProgram\\Python\\sql_handler\\a\\final\\output_final_mv.txt"
    output_final_vw = "D:\\MyProgram\\Python\\sql_handler\\a\\final\\output_final_vw.txt"
    output_final_fu = "D:\\MyProgram\\Python\\sql_handler\\a\\final\\output_final_fu.txt"
    output_final_pr = "D:\\MyProgram\\Python\\sql_handler\\a\\final\\output_final_pr.txt"

    # Mview
    # mview_fix(source_mv, output_file_fix_mv)

    # View
    # view_fix(source_vw, output_file_fix_vw)

    # Function
    # Function_fix(source_fu, output_file_fix_fu)

    # Procedure
    # procedure_fix(source_pr, output_file_fix_pr)

    # Add Comments
    # first element in comment must be object(view or mivew) name in csv, and csv must include column names

    # input_file=source_vw
    # output_file ="D:\\MyProgram\\Python\\sql_handler\\A\\final\\final_with_comment.txt"
    # comment_csv_file = "D:\\MyProgram\\Python\\sql_handler\\A\\comments.csv"
    # add_comments (input_file,output_file,comment_csv_file,schema_name)

    # generate_index (source_mv, output_index_final,TITLE_M_VIEW)
    # text1='test1, to_char(aaa,"yyddmm"),(bbb)::varchar,cc ccc,'
    # text1='upper(to_char(zzz)), lower(to_char(AAA)),to_char(upper(to_char(CCCC)))'
    # text1='to_char(upper(to_char(zzz)))'
    # text1='upper(to_char(zzz)'
    # print("Final: ")
    # print(replace_to_char(text1))

    # get_tree()

    # getObjectList_oracle()
    # getObjectList_redshift()
    # list_all_pr_dependent_objects()

    # test_funcion()
    all_result_test_funcion()
