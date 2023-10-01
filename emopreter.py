import re
import zipfile
import sys,os

def getContentOfODT(odt_file):
    with zipfile.ZipFile(odt_file,'r') as z:
        content = z.read('content.xml')
    utf = content.decode("utf-8")
    return utf

def isComicSans(content_xml):
    style_name_string = "style:style style:name=\""
    style_font_string = "font-name=\""

    style_names=[]
    font_names=[]
    
    first_indexes=[m.start() for m in re.finditer(style_name_string,content_xml)]
    for index in first_indexes:
        style_names += [content_xml[index+len(style_name_string):index+len(style_name_string)+2]]   # style names finden (z.B P1,P2,T1,T2,...)

    first_indexes=[m.start() for m in re.finditer(style_font_string,content_xml)]
    for index in first_indexes:
        font_names += [content_xml[index+len(style_font_string):index+len(style_font_string)+13]]   # zugehörige font names finden (z.B Comic Sans MS)


    dissallowed_styles = []
    for style_name, font_name in zip(style_names,font_names):
        if font_name != "Comic Sans MS":
            dissallowed_styles += [style_name]  # falls font name nicht Comic Sans MS ist, darf style nicht verwendet werden


    text_style_name_string = "text:style-name=\""
    first_indexes=[m.start() for m in re.finditer(text_style_name_string,content_xml)]
    for index in first_indexes:
        if content_xml[index+len(text_style_name_string):index+len(text_style_name_string)+2] in dissallowed_styles:    # falls verwendeter style nicht erlaubt, return False
            return False

    return True

def stripNonEmoji(content_xml):
    only_emojis=re.compile("(["
    "\u2000-\u3300"
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U0001F170-\U0001F19A"  # 🅰 - 🆚
    "])")

    emojis="".join(re.findall(only_emojis,content_xml))
    return emojis

def translateNums(emoji_text):
    zahlen_emo=''.join([ "🅾"[0], "🕐"[0], "🕑"[0], "🕒"[0], "🕓"[0], "🖐🏼"[0], "🕕"[0], "🕖"[0], "🕗"[0], "🕘"[0] ])
    zahlen_ascii = "0123456789"
    zahlen_dict = str.maketrans(zahlen_emo,zahlen_ascii)

    ascii_text = emoji_text.translate(zahlen_dict)
    return ascii_text

def translateAbc(emoji_text):
    abc_emo = ''.join(["🅰"[0],"🅱"[0],"🌶"[0],"🦡"[0],"📧"[0],"🏭"[0],"🍴"[0],"🐓"[0],"ℹ"[0],"🧥"[0],"🕋"[0], "🏷"[0], 
                       "🌽"[0],"🤛🏼"[0],"⭕"[0],"👫"[0],"❇"[0],"🎡"[0],"🚈"[0],"🦖"[0],"🚇"[0],"✌🏼"[0],"⚖"[0],"❎"[0],"💴"[0],"🦷"[0]])
    abc_ascii = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()
    abc_dict = str.maketrans(abc_emo,abc_ascii)

    ascii_text = emoji_text.translate(abc_dict)
    return ascii_text

def translateSymbols(emoji_text):
    symbol_emo = ''.join(["🦴","▶","◀","🌜","🌛","👈🏼"[0],"🔚","👉🏼"[0],"➡","➕","➖","✖","➗","⏭"[0],"⏮"[0],"👆🏼"[0],"🌫"[0]])
    symbol_ascii = ',""()=\n.\t+-*/[]: '
    symbol_dict = str.maketrans(symbol_emo,symbol_ascii)

    ascii_text = emoji_text.translate(symbol_dict)
    return ascii_text

def translateCode(emoji_text):
    emo_to_py_dict={"🖨":"print","🔙":"return ","👇🏼"[0]:"import ","📝":"os","🏠":"system","📥":"input","🏁":"while ","🦵":"continue","❓":"if ","↔":"==",
                    "❌":"else","⁉":"elif ","🛑":"break","🗒":"def "}
    emo_dict = str.maketrans(emo_to_py_dict)

    ascii_text = emoji_text.translate(emo_dict)
    return ascii_text

def stripNonAscii(non_emoji_text):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in non_emoji_text if 0 < ord(c) < 127)
    return ''.join(stripped)

def translateAll(emoji_text):
    ascii_nums = translateNums(emoji_text)
    ascii_abc = translateAbc(ascii_nums)
    ascii_symbol = translateSymbols(ascii_abc)
    ascii_code = translateCode(ascii_symbol)
    return ascii_code

def run(emoji):
    content_xml=getContentOfODT(emoji)  # content.xml aus .odt datei extrahieren

    if not isComicSans(content_xml):
        print("F1337: Das ist nicht alles in Comic Sans MS! so nen Dreck übersetz ich nicht. >:(") # alternativ, falls farben möglich sind: "\x1b[31;20mF1337: Das ist nicht alles in Comic Sans MS! so nen Dreck übersetz ich nicht. >:(\x1b[0m"
        return
    
    emoji_text = stripNonEmoji(content_xml)     # normale ASCII Zeichen entfernen
    emoji_code=translateAll(emoji_text)     # alle übersetzbaren emojis in python code übersetzen
    code = stripNonAscii(emoji_code)    # eventuell nicht übersetzbare emojis entfernen

    code_banner = "-"*50+"\n"+"CODE:\n"+"-"*50
    exec_banner = "-"*50+"\nEXEC:\n"+"-"*50
    print(code_banner+"\n"+code+"\n"+exec_banner)

    with open("trytrans_tmp_532623.py","w") as f:  # python code in datei schreiben
        f.write(code)
    
    os.system("python trytrans_tmp_532623.py && rm trytrans_tmp_532623.py")   #python code ausführen und python datei löschen


if __name__=="__main__":
    if len(sys.argv)<2:
        print("keine Datei angegeben.\nSyntax: python emopiler.py [odt Datei]")
        exit()

    run(sys.argv[1])