import data as D
import random as R
import constants as C


def hi(uid):
    patterns = ['{b_hi}, <@{id}>.', '<@{id}>, {s_hi}.']
    h = R.choice(D.hello)
    return R.choice(patterns).format(id=uid, b_hi=h, s_hi=h.lower())


def welcome_msg(uid):
    return '{0}\n{1} {2}\n{3}'.format(
        hi(uid),
        '{glad_to_see} {glad_ans} {because} {pause_reason} - {pause_wait}'.
            format(glad_to_see=R.choice(D.glad_to_see), glad_ans=R.choice(D.glad_ans),
                   because=R.choice(D.because), pause_reason=R.choice(D.pause_reason),
                   pause_wait=R.choice(D.pause_wait)),
        D.rules_and_ask.format(rules=C.channels['rules'], ask=C.channels['ask']),
        R.choice(D.welcome_finish)
    )


def comeback_msg(uid, time_out=False, clan_id=False):
    return '{0} {1}{2}'.format(R.choice(D.comeback_msg).format(name=uid),
                               D.comeback_time[time_key(time_out)] or '',
                               clan_id and '\n{0}'.format(R.choice(D.comeback_clan).format(clan=clan_id)) or ''
                               )


def time_key(t):
    if not t:
        return False

    if t < 60:
        return 'min'
    elif t < 3600:
        return 'hour'
    elif t < 86400:
        return 'day'
    elif t < 604800:
        return 'week'
    elif t < 18144000:
        return 'month'
    elif t < 220752000:
        return 'year'
    else:
        return 'years'


def bye_msg(uid):
    patterns = ['{b_bye}, <@{id}>.', '<@{id}>, {s_bye}.']
    b = R.choice(D.bye)
    return '{pattern}\n{phrase}'.format(pattern=R.choice(patterns).format(id=uid, b_bye=b, s_bye=b.lower()),
                                        phrase=R.choice(D.bye_phrase))


def ban_msg(uid):
    return '{msg}\n{comment}'.format(msg=R.choice(D.ban_msg).format(name=uid), comment=R.choice(D.ban_comment))


def unban_msg(uid):
    return '{msg}\n{comment}'.format(msg=R.choice(D.unban_msg).format(name=uid), comment=R.choice(D.unban_comment))
