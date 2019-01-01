import re
import hashlib
import data as D
import random as R
import constants as C
import emj
import other
import log


good_time = {}
morning_add = {}
resp_keys = {}
resp_values = {}
resp_data = {}


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

    log.jI('\t -make resp_keys')
    # searching resp_keys can be done with regex, but test show,
    # that intersection with set(words) and "in"-check(collocations) in for-cycle are faster (≈ in 10 times)
    for key in D.dataKeys:
        keys = D.dataKeys[key]
        dct = {'words': set(), 'colls': set()}
        if isinstance(keys, dict):
            if 'clear' in keys:
                dct['words'].update(keys['clear'])
            if 'noun' in keys:
                dct['words'].update(make_words(keys['noun'], D.noun_endings))
            if 'adj' in keys:
                dct['words'].update(make_words(keys['adj'], D.adj_endings))
            if 'eng' in keys:
                dct['words'].update(make_words(keys['eng'], D.eng_endings))
            if 'clear_collocation' in keys:
                dct['colls'].update(keys['clear_collocation'])
            if 'n_c' in keys:
                for coll in keys['n_c']:
                    dct['colls'].update(make_words(make_words([coll[0]], D.noun_endings), [' ' + coll[1]]))
            if 'a_c' in keys:
                for coll in keys['a_c']:
                    dct['colls'].update(make_words(make_words([coll[0]], D.adj_endings), [' ' + coll[1]]))
        else:
            dct['words'].update(keys)
        resp_keys[key] = dct
    log.jI('\t -make resp_values & resp_data')
    for key in D.responses:
        resp_values[key] = []
        for phr in D.responses[key]:
            if isinstance(phr, str):
                h = hashlib.md5(phr.encode('utf-8')).hexdigest()
                resp_data[h] = {'text': phr}
                resp_values[key] += [h]
            else:
                if not (isinstance(phr, dict) and 'text' in phr):
                    log.jW('fail phrase in response data: ', phr)
                else:
                    h = hashlib.md5(phr['text'].encode('utf-8')).hexdigest()
                    resp_data[h] = phr
                    resp_values[key] += [h]

    log.I('Prepare communication done.')


def check_phrase(phr, words):
    f_keys = []
    for key in resp_keys:
        f_key = resp_keys[key]['words'].intersection(words)
        if not f_key:
            for coll in resp_keys[key]['colls']:
                f_key = coll in phr
                if f_key:
                    break

        if f_key:
            f_keys += [key]

    return f_keys


def get_resp(keys):
    key = R.choice(keys)
    answers = resp_values[key]
    ans_phr = resp_data[R.choice(answers)]
    return ans_phr


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
    smiles = re.findall(r'[:][\w_]*[:]', orig_phrase)
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


def bye(uid, name=''):
    return other.name_phr(uid, R.choice(D.bye), name=name)


def bye_msg(uid, name=''):
    return '{bye}\n{phrase}'.format(bye=bye(uid, name), phrase=R.choice(D.bye_phrase))


def ban_msg(uid, nick=''):
    nick = nick and '(' + nick + ')'
    name = '<@{uid}>{nick}'.format(uid=uid, nick=nick)
    return '{msg}\n{comment}'.format(msg=R.choice(D.ban_msg).format(name=name), comment=R.choice(D.ban_comment))


def unban_msg(uid):
    return '{msg}\n{comment}'.format(msg=R.choice(D.unban_msg).format(name=uid), comment=R.choice(D.unban_comment))


def make_words(words, endings):
    s = set()
    for w in words:
        for end in endings:
            s.add(w + end)

    return s


def voice_event(user, channel):
    return R.choice(D.voice_alone_messages).format(user='<@'+user.id+'>', voice='<#'+channel.id+'>')


def voice_note(user):
    if user.id in D.voice_notions:
        return R.choice(D.voice_notions[user.id]).format(user='<@' + user.id + '>')
    else:
        return False

