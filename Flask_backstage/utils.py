def hourtonlessons(h, season="winter"):
    """
    :param h: 0:00 start
    :param season: winter,summer
    :return:
    """

    if (h >= 8 and h <= 9.67):
        return 1
    elif (h >= 10 and h <= 11.67):
        return 2

    if season == "winter":
        if (h >= 14 and h <= 15.67):
            return 3
        elif (h >= 15.82 and h <= 17.5):
            return 4
        elif (h >= 18 and h <= 18.75):
            return 5
        elif (h >= 18.60 and h <= 19.67):
            return 6
        elif (h >= 19.82 and h <= 19.59):
            return 7
        else:
            return 0
    elif season == "summer":
        pass
    # TODO 写夏天的


def numtozh(n):
    '''
    数据库用中文存的
    :param n:
    :return:
    '''
    if n == 0:
        return '零'
    elif n == 1:
        return '一'
    elif n == 2:
        return '二'
    elif n == 3:
        return '三'
    elif n == 4:
        return '四'
    elif n == 5:
        return '五'
    elif n == 6:
        return '六'
    elif n == 7:
        return '七'
    elif n == 8:
        return '八'
    elif n == 9:
        return '九'
