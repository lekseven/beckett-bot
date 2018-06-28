import re
import data as D
import random as R
import constants as C
import emj
import other
import log


good_time = {}
morning_add = {}


def prepare():
    log.I('Prepare communication:')
    log.jI('\t -make dictionary good_type')
    for g_key in D.good_time:
        g_period = []
        for d_type in D.good_time[g_key]:
            g_type = {'simple': set(d_type['simple']), 'check_phrases': [], 'response': []}
            if 'key' in d_type:
                for noun in d_type['key']['noun']:
                    for adj in d_type['key']['adj']:
                        g_type['check_phrases'].append(noun + ' ' + adj)
                        g_type['check_phrases'].append(adj + ' ' + noun)

            for noun in d_type['noun']:
                for adj in d_type['adj']:
                    g_type['check_phrases'].append(noun + ' ' + adj)
                    g_type['check_phrases'].append(adj + ' ' + noun)
                    g_type['response'].append(adj + ' ' + noun)
                    # g_type['response'].append(adj.title() + ' ' + noun + ', <@{name}>.')
                    # g_type['response'].append('<@{name}>, ' + adj + ' ' + noun + '.')
            g_period.append(g_type)
        good_time[g_key] = g_period
    log.jI('\t -make morning add')
    morn_add = {
        'Kuro': ':tea:', 'Natali': ':tea::chocolate_bar:', 'Soul': ':coffee:',
        'Buffy': ':sun_with_face:', 'Tilia': ':sun_with_face:',
        'Doriana': ':hugging:', 'Creol': ':hugging:',
    }
    for name in morn_add:
        if name in C.users:
            morning_add[C.users[name]] = morn_add[name]
    log.I('Prepare communication done.')


def f_gt_key(orig_phrase, tr_phrase, words, bot_mention):
    """

    :type orig_phrase: basestring
    :type tr_phrase: basestring
    :type words: set
    :param bot_mention: bool
    """
    words.difference_update(emj.em_set)
    ignore = {'вам', 'всем'}
    words.difference_update(ignore)
    skin_sm = set()
    for w in words:
        if set(w).intersection(emj.skins_set):
            skin_sm.add(w)
    words.difference_update(skin_sm)

    if (orig_phrase.count('@') > 0 and not bot_mention) or len(words) < 1:
        return False

    phr = re.sub('[ ]?' + '|'.join(ignore) + '[ ]?', ' ', tr_phrase)  # delete all words from ignore
    phr = re.sub('[ ]+', ' ', phr)  # replace more than one spaces with only one
    smiles = re.findall('[:][\w_]*[:]', orig_phrase)
    count_sm = len(smiles) + ''.join(smiles).count('_')
    simple = len(words) < (count_sm + 2 + bot_mention)

    for g_key in good_time:
        i = 0
        for g_type in good_time[g_key]:
            if simple and words.intersection(g_type['simple']):
                return {'g_key': g_key, 'g_type': i}

            for ch_phr in g_type['check_phrases']:
                if ch_phr in phr:
                    return {'g_key': g_key, 'g_type': i}

            i += 1

    return False


def hi(uid):
    return other.name_phr(uid, R.choice(D.hello))


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


def bye(uid):
    return other.name_phr(uid, R.choice(D.bye))


def bye_msg(uid):
    return '{bye}\n{phrase}'.format(bye=bye(uid), phrase=R.choice(D.bye_phrase))


def ban_msg(uid):
    return '{msg}\n{comment}'.format(msg=R.choice(D.ban_msg).format(name=uid), comment=R.choice(D.ban_comment))


def unban_msg(uid):
    return '{msg}\n{comment}'.format(msg=R.choice(D.unban_msg).format(name=uid), comment=R.choice(D.unban_comment))
