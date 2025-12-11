import re

def linkFiner(val:str)->tuple:
    '''
    :param val: string with club id on transfermarkt
    :return: corrected link with last actual squad \ raise error
    '''
    try:
        val = re.findall(r'\d+',val)[0]
        return ('https://www.transfermarkt.com/defualt/startseite/verein/'+val, val)
    except:
        print(f'Your input: {val}\n',
              'It should contains digit-identificator of club',
              r'like this: https://www.transfermarkt.com/sokol-saratov/startseite/verein/3834 \n')
        raise NameError('Wrong team link!')

def posFiner(val:str)->str:
    '''
    :param val: long-name of position
    :return res: short-name of position
    '''
    helpDict = {'Goalkeeper':'GK','Defender':'DEF','Midfield':'MID','Attack':'ATK'}

    if val in helpDict:
        return helpDict[val]
    else:
        return val
