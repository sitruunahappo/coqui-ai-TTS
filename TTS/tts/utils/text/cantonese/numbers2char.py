#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Licensed under WTFPL or the Unlicense or CC0.
# This uses Python 3, but it's easy to port to Python 2 by changing
# strings to u'xx'.

# Basically copied from the one for Mandarin, but I suppose:
# 1) We use 「兩」 more than 「二」 when appropriate 
# 2) We use traditional characters more for some reasons
# 3) Most of the time we use 「廿」 for 20 instead of 「二十」
#
# Haven't tested it completely as my dataset includes no digits 
# for converting

import itertools
import re


def _num2chinese(num: str, big=False, simp=False, o=False, twoalt=True, jaa=True) -> str:
    """Convert numerical arabic numbers (0->9) to chinese hanzi numbers (〇 -> 九)

    Args:
        num (str): arabic number to convert
        big (bool, optional): use financial characters. Defaults to False.
        simp (bool, optional): use simplified characters instead of tradictional characters. Defaults to True.
        o (bool, optional): use 〇 for 'zero'. Defaults to False.
        twoalt (bool, optional): use 两/兩 for 'two' when appropriate. Defaults to False.

    Raises:
        ValueError: if number is more than 1e48
        ValueError: if 'e' exposent in number

    Returns:
        str: converted number as hanzi characters
    """

    # check num first
    nd = str(num).replace(',', '')
    
    if abs(float(nd)) >= 1e48:
        raise ValueError("number out of range")
    if "e" in nd:
        raise ValueError("scientific notation is not supported")

    c_symbol = "正负点" if simp else "正負點"
    
    if o:  # formal
        twoalt = False
    
    if big:
        c_basic = "零壹贰叁肆伍陆柒捌玖" if simp else "零壹貳參肆伍陸柒捌玖"
        c_unit1 = "拾佰仟"
        c_twoalt = "贰" if simp else "貳"
    else:
        c_basic = "〇一二三四五六七八九" if o else "零一二三四五六七八九"
        c_unit1 = "十百千"
        if twoalt:
            c_twoalt = "两" if simp else "兩"
        else:
            c_twoalt = "二"
    
    c_unit2 = "万亿兆京垓秭穰沟涧正载" if simp else "萬億兆京垓秭穰溝澗正載"
    revuniq = lambda l: "".join(k for k, g in itertools.groupby(reversed(l)))  # Is it good to use lambda not anonymous?
    nd = str(num).replace(',', '')
    result = []

    if nd[0] == "+":
        result.append(c_symbol[0])
    elif nd[0] == "-":
        result.append(c_symbol[1])
    
    if "." in nd:
        integer, remainder = nd.lstrip("+-").split(".")
    else:
        integer, remainder = nd.lstrip("+-"), None
    
    if int(integer):
        splitted = [integer[max(i - 4, 0) : i] for i in range(len(integer), 0, -4)]
        intresult = []
        for nu, unit in enumerate(splitted):
            # special cases
            if int(unit) == 0:  # 0000
                intresult.append(c_basic[0])
                continue
            if nu > 0 and int(unit) == 2:  # 0002
                intresult.append(c_twoalt + c_unit2[nu - 1])
                continue
        
            ulist = []
            unit = unit.zfill(4)
            for nc, ch in enumerate(reversed(unit)):
                if ch == "0":
                    if ulist:  # ???0
                        ulist.append(c_basic[0])
                elif nc == 0:
                    ulist.append(c_basic[int(ch)])
                elif nc == 1 and ch == "1" and unit[1] == "0":
                    # special case for tens
                    # edit the 'elif' if you don't like
                    # 十四, 三千零十四, 三千三百一十四
                    ulist.append(c_unit1[0])
                elif nc > 1 and ch == "2":
                    ulist.append(c_twoalt + c_unit1[nc - 1])
                else:
                    ulist.append(c_basic[int(ch)] + c_unit1[nc - 1])
        
            ustr = revuniq(ulist)
            if nu == 0:
                intresult.append(ustr)
            else:
                intresult.append(ustr + c_unit2[nu - 1])
        
        result.append(revuniq(intresult).strip(c_basic[0]))
    else:
        result.append(c_basic[0])
    
    if remainder:
        result.append(c_symbol[2])
        result.append("".join(c_basic[int(ch)] for ch in remainder))

    result_str = "".join(result)
    
    if jaa:
        result_str = result_str.replace('二十', '廿')

    return result_str


def _year2chinese(num: str, big=False, simp=False, o=False) -> str:
    '''Only apply to year

    Same setting as above
    I do think that sometime people will use 廿, but I don't think 
    it frequent 
    '''
    num = num.replace('年', '')
    if big:
        c_basic = "零壹贰叁肆伍陆柒捌玖" if simp else "零壹貳參肆伍陸柒捌玖"
    else:
        c_basic = "〇一二三四五六七八九" if o else "零一二三四五六七八九"
    
    result = ''
    for d in str(num):
        result += c_basic[int(d)]

    return result + '年'


def _number_replace(match) -> str:
    """function to apply in a match, transform all numbers in a match by chinese characters

    Args:
        match (re.Match): numbers regex matches

    Returns:
        str: replaced characters for the numbers
    """
    match_str: str = match.group()

    if '年' in match_str:
       return _year2chinese(match_str) 
    else:
        return _num2chinese(match_str)


def replace_numbers_to_characters_in_text(text: str) -> str:
    """Replace all arabic numbers in a text by their equivalent in chinese characters (simplified)

    Args:
        text (str): input text to transform

    Returns:
        str: output text
    """
    text = text.replace(' ', '')  # It is usually safe to remove spaces for a Chinese language 
    text = re.sub(r'(?:\d+,?\.?)+年?', _number_replace, text)

    return text


if __name__ == '__main__':
    test_1 = '香港管轄總面積2,755.03平方公里'
    test_2 = '買20個蘋果'
    test_3 = '2024年年底香港人口的臨時數字為7 534 200人'

    # 香港管轄總面積兩千七百五十五點零三平方公里
    print(replace_numbers_to_characters_in_text(test_1))

    # 買廿個蘋果
    print(replace_numbers_to_characters_in_text(test_2))

    # 二零二四年年底香港人口的臨時數字為七百五十三萬四千兩百人
    print(replace_numbers_to_characters_in_text(test_3))
