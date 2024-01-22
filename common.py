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

        with open(input_file, 'r') as infile:
            for line in infile:
                line = line.lower()
                if line.startswith("create ") and schema_name in line:
                    # save the last block
                    if current_Original_SQL != "":
                        # format sql for simple SQL
                        pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
                        current_simple_SQL = re.sub(
                            pattern, '', current_simple_SQL)
                        current_simple_SQL = current_simple_SQL.lower()

                        current_simple_SQL = re.sub(
                            r"\s+from\s+\(", " from(", current_simple_SQL)
                        current_simple_SQL = re.sub(
                            r"\s+join\s+\(", " join(", current_simple_SQL)

                        # current_simple_SQL = re.sub(
                        #     r'from.*?\(', 'from(', current_simple_SQL)
                        # current_simple_SQL = re.sub(
                        #     r'join.*?\(', 'join(', current_simple_SQL)

                        # current_simple_SQL = current_simple_SQL.replace(
                        #     'from (', 'from(')
                        # current_simple_SQL = current_simple_SQL.replace(
                        #     'join (', 'join(')

                        # current_simple_SQL = current_simple_SQL.replace(
                        #     'from (', 'from(')
                        # current_simple_SQL = current_simple_SQL.replace(
                        #     'join (', 'join(')

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
                if '--' in temp_str:
                    temp_str = temp_str[:temp_str.find('--')]

                current_simple_SQL += temp_str.strip().replace("\n", " ").replace("\t",
                                                                                  " ").replace("  ", " ")+" "

            if current_Original_SQL != "":
                results.append(
                    [current_object_name, current_Original_SQL, current_simple_SQL])
        return results
    except IOError as e:
        raise IOError(f"Error copying file: {e}")


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
                    " natural ", " over ", " partition by ", " join"]
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


"""
TODO:
def get_table_from_insert_into(one_object_simple_sql): get all tables from 'insert into' from one object
return 2-d array:
1. [inser_into_object_name]
2. [tables name]

def get_table_from_update_set(one_object_simple_sql): get all tables i all 'update set' from one object
return 2-d array:
1. [update_set_object_name]
2. [tables name]

"""

# def get_table_in_one_insert_into_sql_statement(text):
#     """
#         input must be single insert_into sql statement
#         Get all tables from one one insert_into sql object statement
#         call get_table_in_one_sql_statement() function

#         return array:
#         1. [insert into table name]
#         1. [table names]
#     """
#     print("get_table_in_one_insert_into_sql_statement: " + text)
#     # set condition
#     # just handle insert into and update set
#     TC = "insert into "
#     results = []
#     if TC in text:
#         new_line = text.lower()
#         results = rec_get_table_from_blackset(new_line)

#         # for result in results:
#         #     print(result)
#     return results


# recuive to find string


def rec_get_table_from_blackset(input_str):
    # From block
    TC1 = ' from('
    results = []
    ii = input_str.find(TC1)

    if ii > -1:
        temp_str = input_str[ii+len(TC1):-1]
        temp_str = temp_str.strip()
        if temp_str[:-1] != ')':
            return results
        temp_str = temp_str[:-1]
        print("temp_str: "+temp_str)
        current_results = rec_get_table_from_blackset(input_str)
        for current_result in current_results:
            results.append(current_result)
        return results
    else:
        TC2 = ' from '
        return results

    # # Join Block
    # rest_str = input_str

    # block_end_index = -1
    # tochar_index = rest_str.find(TC+"(")

    # if tochar_index < 0:
    #     tochar_index = rest_str.find(TC+" (")

    # if tochar_index > -1:
    #     rest_str = rest_str[tochar_index:]

    #     i = 0
    #     has_comma = False

    #     for j, char in enumerate(rest_str):
    #         if i == 1 and char == ',':
    #             has_comma = True
    #         if char == '(':
    #             i += 1
    #         if char == ')':
    #             i -= 1
    #             block_end_index = j+1

    #             if i == 0:
    #                 if has_comma == False:
    #                     new_block = rest_str[:block_end_index]
    #                     results.append(new_block)

    #                     new_tochar_index = new_block.find(TC+"(")

    #                     if new_tochar_index < 0:
    #                         new_tochar_index = new_block.find(TC+" (")

    #                     if new_tochar_index > -1:
    #                         sub_results = get_to_char_string(
    #                             new_block[len(TC):])
    #                         for sub_result in sub_results:
    #                             results.append(sub_result)

        # rest_str=rest_str[block_end_index+1:]
        # break

    # if block_end_index==-1:
    #     break
    return results


def get_table_at_from_block(input_str):
    print("get_table_at_from_block")
