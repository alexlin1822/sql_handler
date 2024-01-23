import re
import sys

TITLE_TABLE = 'CREATE TABLE'.lower()
TITLE_VIEW = 'create or replace view'.lower()
TITLE_M_VIEW = 'create materialized view'.lower()
TITLE_PROCEDURE = 'CREATE PROCEDURE'.lower()
TITLE_FUNCTION = 'CREATE OR REPLACE FUNCTION'.lower()


def get_object_name(input):
    """
        (Tested)
        Get the object name 
    """

    input = input.strip().lower()
    if input.startswith(TITLE_TABLE):
        start_index = len(TITLE_TABLE)
        end_keyword = "("
    elif input.startswith(TITLE_VIEW):
        start_index = len(TITLE_VIEW)
        end_keyword = "("
    elif input.startswith(TITLE_M_VIEW):
        start_index = len(TITLE_M_VIEW)
        end_keyword = " as"
    elif input.startswith(TITLE_PROCEDURE):
        start_index = len(TITLE_PROCEDURE)
        end_keyword = "("
    elif input.startswith(TITLE_FUNCTION):
        start_index = len(TITLE_FUNCTION)
        end_keyword = "("
    else:
        return ""

    title = input[start_index:]
    end_index = title.find(end_keyword)
    if end_index > -1:
        return title[:end_index].strip()
    else:
        return title.strip()


def get_insert_into_object_name(line):
    """
        (Tested)
        Get a table name from 'insert into' 
    """

    inst_str = ""
    inst = line.lower().find("insert into ")

    if inst > -1:
        inst_str = line.lower()[inst+len("insert into "):]
        inst_str = inst_str.strip()
        inst_str_aa = inst_str
        inst_str_bb = inst_str

        aa = inst_str_aa.find(" ")
        bb = inst_str_bb.find("(")

        if (aa > -1):
            inst_str_aa = inst_str_aa[:aa].strip()

        if (bb > -1):
            inst_str_bb = inst_str_bb[:bb].strip()

        if len(inst_str_aa) < len(inst_str_bb):
            inst_str = inst_str_aa
        else:
            inst_str = inst_str_bb

        if inst_str.strip() == "'":
            inst_str = 'v_uscomm_table'

        if inst_str[-1:] == '\n':
            inst_str = inst_str[:-1]

        # print("inst line: "+ inst_str)

    return inst_str


def get_update_object_name(line):
    """
        (Tested)
        Get a table name from 'update ' 
    """

    inst_str = ""
    inst = line.lower().find("update ")

    if inst > -1:
        inst_str = line.lower()[inst+len("update "):]
        inst_str = inst_str.strip()
        inst_str_aa = inst_str
        inst_str_bb = inst_str

        aa = inst_str_aa.find("set ")

        if aa > -1:
            inst_str = inst_str_aa[:aa].strip()

        if inst_str[-1:] == '\n':
            inst_str = inst_str[:-1]

        # print("inst line: "+ inst_str)

    return inst_str


def split_object(input_file, object_type, schema_name):
    """
    Tested!
    def split_object(text,object_type): read file and spile to object
        return 2-d array:
        1. object name
        2. object Original SQL
        3. object simple SQL (no comment, no tab, no '\n')
    """
    schema_name = schema_name.lower()
    try:
        results = []
        current_object_name = ""
        current_Original_SQL = ""
        current_simple_SQL = ""
        in_comment_block = 0

        with open(input_file, 'r') as infile:
            for line in infile:
                line = line.lower()
                if line.startswith("create ") and schema_name in line:
                    # save the last block
                    if current_Original_SQL != "":
                        # format sql for simple SQL
                        current_simple_SQL = format_simple_sql(
                            current_simple_SQL)

                        # save the last block
                        results.append(
                            [current_object_name, current_Original_SQL.strip(), current_simple_SQL.strip()])

                        current_object_name = ""
                        current_Original_SQL = ""
                        current_simple_SQL = ""

                    # start new block
                    current_object_name = get_object_name(line)

                # load each line
                current_Original_SQL += line
                temp_str = line

                # delete comment
                if in_comment_block > 0:
                    has_comment_block = temp_str.find('/*')
                    has_comment_block_end = temp_str.find('*/')
                    if has_comment_block == -1:
                        has_comment_block = sys.maxsize
                    if has_comment_block_end == -1:
                        has_comment_block_end = sys.maxsize

                    if has_comment_block < has_comment_block_end:
                        in_comment_block += 1
                    elif has_comment_block > has_comment_block_end:
                        in_comment_block -= 1
                        temp_str = temp_str[:has_comment_block] + \
                            temp_str[has_comment_block_end+2:]
                    else:
                        temp_str = ""

                if in_comment_block == 0:
                    has_comment_block = temp_str.find('/*')
                    has_comment_block_right = temp_str.find('--')
                    if has_comment_block == -1:
                        has_comment_block = sys.maxsize
                    if has_comment_block_right == -1:
                        has_comment_block_right = sys.maxsize

                    if has_comment_block < has_comment_block_right:    # handle /*
                        temp_str = temp_str[:has_comment_block]
                        rest_str = temp_str[has_comment_block+2:]

                        while (rest_str != "" and in_comment_block > 0):
                            has_comment_block = rest_str.find('/*')
                            has_comment_block_end = rest_str.find('*/')
                            if has_comment_block == -1:
                                has_comment_block = sys.maxsize
                            if has_comment_block_end == -1:
                                has_comment_block_end = sys.maxsize

                            if has_comment_block < has_comment_block_end:
                                in_comment_block += 1
                                rest_str = rest_str[has_comment_block+2:]
                            elif has_comment_block > has_comment_block_end:
                                in_comment_block -= 1
                                rest_str = rest_str[has_comment_block_end+2:]
                            else:
                                rest_str = ""

                    else:  # handle --
                        temp_str = temp_str[:has_comment_block_right]

                # delete others i.e \n \t " "
                current_simple_SQL += temp_str.strip().replace("\n", " ").replace("\t",
                                                                                  " ").replace("  ", " ")+" "

            if current_Original_SQL != "":
                # format sql for simple SQL
                current_simple_SQL = format_simple_sql(current_simple_SQL)

                # save the last block
                results.append(
                    [current_object_name, current_Original_SQL, current_simple_SQL])
        return results
    except IOError as e:
        raise IOError(f"Error copying file: {e}")


def format_simple_sql(input_str):
    """ 
    (Tested)
        Format simple sql
        'from ('    -> 'from('
        'join ('    -> 'join('
    """
    current_simple_SQL = input_str
    current_simple_SQL = current_simple_SQL.lower()
    current_simple_SQL = re.sub(r"\s+from\s+\(", " from(", current_simple_SQL)
    current_simple_SQL = re.sub(r"\s+join\s+\(", " join(", current_simple_SQL)
    return current_simple_SQL


def split_statement_using_semiqute_for_one_object(text_single_object):
    """
        Tested!
        input must be single object which getting from spile_object([simple SQL [2]]) 
        Split string by ";"
        return array:
        1. [statements]
    """
    results = []
    text = text_single_object.lower()

    new_text = text[text.find("begin")+5:text.find("end;")]
    new_text = new_text.strip()

    if ";" in new_text:
        results = new_text.split(";")
        results = [element.strip() for element in results]
        results = [item.strip() for item in results if item.strip() != ""]
    else:
        results.append(new_text.strip())
    return results


def get_table_in_one_sql_statement_rec(text, results):
    """
        (Tested)
        Get all tables from one one sql object statement
        input must be single sql statement (i.e one select, or one insert into, or one update set)
        return array:
        1. [table names]
    """
    new_results = []
    for result in results:
        new_results.append(result)

    # print("get_table_in_one_sql_statement: " + text)

    keywords = [" from(", " join(", " from ",  " join "]
    sql_str = text.lower()
    ii = 0
    while (sql_str.strip() != ""):
        positions = []
        for keyword in keywords:
            positions.append(-1)

        min = sys.maxsize
        min_index = -1

        for i, keyword in enumerate(keywords):
            positions[i] = sql_str.find(keyword)
            if positions[i] > -1 and positions[i] < min:
                min = positions[i]
                min_index = i

        if min_index == -1:
            break
        elif min_index == 0 or min_index == 1:    # 'from('  or 'join('
            sql_str = sql_str[min+len(keywords[min_index])-1:]
            end_index = get_end_blanket_index(sql_str)
            if end_index == -1:
                print("------------------")
                print("error: No end blanket index")
                print("SQL: "+sql_str)
                print("------------------")
                break
            rec_str = sql_str[1:end_index]
            rec_results = get_table_in_one_sql_statement_rec(rec_str, results)

            for rec_result in rec_results:
                new_results.append(rec_result)

            sql_str = sql_str[end_index+1:]

        elif min_index == 2 or min_index == 3:  # from or # join
            sql_str = sql_str[min+len(keywords[min_index]):]
            end_index = -1
            if min_index == 2:    # from
                end_index = get_end_keyword_index(sql_str, "from")
            else:                 # join
                end_index = get_end_keyword_index(sql_str, "join")
            # print("# end_index: "+str(end_index))
            tables = []
            tables_str = ""
            if end_index > -1:
                tables_str = sql_str[:end_index]
                sql_str = sql_str[end_index:].strip()
            else:
                tables_str = sql_str
                sql_str = ""

            # print("# from tables_str: "+tables_str)
            # print("# from rest : "+sql_str)

            tables = tables_str.split(",")

            for table in tables:
                table_name = table.strip().split(" ")[0]
                new_results.append(table_name)
                # print("# table name: "+table_name)

    return new_results


def get_end_keyword_index(text, type):
    """
    (Tested)
        Get end index for 'from' or 'join'
        keyword for 'from' or 'join' please check and updates keywords array
        return -1 if not found
    """
    min = sys.maxsize
    sql_str = text.lower()
    keywords = []

    if type == "from":
        keywords = [" where ", " group by ", " order by ", " limit ", " offset ", " having ", " union ", " intersect ", " except ", " on ", " as ",
                    " left join", " left outer join", " right join", " right outer join", " self join",
                    " full outer join", " full join", " inner join", " outer join", " cross join",
                    " natural ", " over ", " partition by ", " join", ")"]
    elif type == "join":
        keywords = [" on ", " as ",
                    " left join", " left outer join", " right join", " right outer join", " self join",
                    " full outer join", " full join", " inner join", " outer join", " cross join",
                    " natural ", " over ", " partition by ", " join"]
    else:
        return -1

    positions = []
    for keyword in keywords:
        positions.append(-1)

    for i, keyword in enumerate(keywords):
        positions[i] = sql_str.find(keyword)
        if positions[i] > -1 and positions[i] < min:
            min = positions[i]
    if min == sys.maxsize:
        min = -1
    return min


def get_end_blanket_index(text):
    """
    (Tested)
        Get end index of blanket
        return -1 if not found
    """
    i = 0
    for j, char in enumerate(text):
        if char == '(':
            i += 1
        if char == ')':
            i -= 1
            if i == 0:
                return j
    return -1
