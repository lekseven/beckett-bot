import re
from hashlib import md5 as hashlib__md5
from importlib import reload as importlib__reload
from lxml.html import fromstring as lxml__fromstring
from requests import get as requests__get
from string import whitespace as string__whitespace

import constants as C
import emj
import other
import log

import d.data_to_process as d2p
import d.data_to_use as d2u
from d import data_com

msg_queue = {}
msg_args = {}
msg_type_count = {}


def make_d2u():
    log.I('<make_d2u>')

    log.jI('\t -make dictionary good_type')
    good_time = {}

    def _make_gt_phrases(phrases, obj2save=None, resp=False):
        obj2save = obj2save or {'simple': set(), 'check_phrases': [], 'response': []}
        if not phrases:
            return obj2save
        if 'simple' in phrases:
            obj2save['simple'].update(phrases['simple'])
        for noun in phrases['noun']:
            for adj in phrases['adj']:
                n_a = ' '.join((noun, adj))
                a_n = ' '.join((adj, noun))
                obj2save['check_phrases'].append(n_a)
                obj2save['check_phrases'].append(a_n)
                if resp:
                    obj2save['response'].append(a_n)
        return obj2save

    for g_key in d2p.good_time:
        g_period = []
        for d_type in d2p.good_time[g_key]:
            gt_type = {}
            if 'key' in d_type:
                gt_type = _make_gt_phrases(d_type['key'])
            gt_type = _make_gt_phrases(d_type, gt_type, resp=True)
            gt_type = {
                'simple': gt_type['simple'],
                'check_phrases': tuple(gt_type['check_phrases']),
                'response': tuple(gt_type['response'])
            }
            g_period.append(gt_type)
        good_time[g_key] = tuple(g_period)

    log.jI('\t -make resp_keys')
    resp_keys = {}

    # searching resp_keys can be done with regex, but test show,
    # that intersection with set(words) and "in"-check(collocations) in for-cycle are faster (≈ in 10 times)

    def _make_words(words, endings):
        s = set()
        for w in words:
            s.update({f'{w}{end}' for end in endings})

        return s

    for ind, keys in d2p.response_keys.items():
        dct = {'words': set(), 'colls': set()}
        dct['words'].update(keys.clear)
        dct['words'].update(_make_words(keys.noun, d2p.noun_endings))
        dct['words'].update(_make_words(keys.adj, d2p.adj_endings))
        dct['words'].update(_make_words(keys.eng, d2p.eng_endings))
        dct['colls'].update(keys.clear_collocation)
        for coll in keys.n_c:
            dct['colls'].update({f'{coll[0]}{end} {coll[1]}' for end in d2p.noun_endings})
        for coll in keys.a_c:
            dct['colls'].update({f'{coll[0]}{end} {coll[1]}' for end in d2p.adj_endings})

        resp_keys[ind] = dct

    log.jI('\t -make resp_values & resp_data')
    resp_values = {}  # keys: {hashes}
    resp_data = {}  # hash : text object {'text':"", etc}

    def _make_resp(obj: (dict, list, tuple, set, str), add_keys: set = None):
        importlib__reload(d2p)
        add_keys = add_keys or set()
        add_phr = {}
        if isinstance(obj, str):
            add_phr = {'text': obj}
        elif isinstance(obj, list) or isinstance(obj, set) or isinstance(obj, tuple):
            for phr in obj:
                _make_resp(phr, add_keys)
        elif isinstance(obj, dict) and 'text' not in obj:
            for key in obj:
                _make_resp(obj[key], add_keys.union({key}))
        elif isinstance(obj, dict) and 'text' in obj:
            add_phr = obj
            add_phr['text'] = str(add_phr['text'])
        else:
            log.jW('<make_d2u.make_resp> Fail phrase in response data: ', obj)

        if add_phr:
            h = hashlib__md5(add_phr['text'].encode('utf-8')).hexdigest()
            add_phr['keys'] = set(add_phr.get('keys', set())).union(add_keys)
            if h in resp_data:
                add_phr['keys'].update(resp_data[h]['keys'])
            resp_data[h] = add_phr
            for key in add_phr['keys']:
                resp_values.setdefault(key, set()).add(h)

    _make_resp(d2p.data_text)
    log.jI('\t -save to d2u.py')
    data_used = []
    saved_args = ('data_used', 'good_time', 'resp_keys', 'resp_values', 'resp_data')
    l_args = locals()
    time_upd = other.t2s(frm="%d/%m/%y %H:%M:%S")
    with open('d/data_to_use.py', "w") as file:
        print('"""\nThis document was created from data_to_process.py by command !data_process'
              f'\nDon\'t edit it by yourself.\nCreated: {time_upd}.\n"""\n\n', file=file)
        print(*(f'{name} = {repr(l_args[name])}' for name in saved_args), file=file, sep='\n\n')
        print(f'\n\nprint("<!>\\t\\tGenerated module data_to_use from {time_upd} was successfully loaded.")', file=file)
    log.I('Reload module d2u...')
    importlib__reload(d2u)
    log.I('Prepare make_d2u done.')


def check_phrase(phr, words):
    f_keys = set()
    for key in d2u.resp_keys:
        f_key = d2u.resp_keys[key]['words'].intersection(words)
        if not f_key:
            for coll in d2u.resp_keys[key]['colls']:
                f_key = coll in phr
                if f_key:
                    break

        if f_key:
            f_keys.add(key)

    return f_keys


'''
def get_resp(keys):
    error_ans = {'text': '', 'last_key': ''}
    if not keys:
        log.E('<com.get_resp> There are no keys!')
        return error_ans

    key = keys if isinstance(keys, str) else other.choice(tuple(keys))
    if key not in resp_values:
        if not isinstance(keys, str):
            new_keys = tuple(k for k in keys if k in resp_values)
            log.E(f'<com.get_resp> There are no key "{key}" try one from {len(new_keys)} keys (all: {len(keys)}).')
            return get_resp(new_keys)
        else:
            log.E(f'<com.get_resp> There are no key "{key}"!')
            return error_ans
    elif not resp_values[key]:
        log.E(f'<com.get_resp> resp_values["{key}"] is empty!')
        return error_ans

    if len(resp_values[key]) == 1:
        d_key = resp_values[key][0]
        resp_data[d_key]['last_key'] = key
        return resp_data[d_key]

    answers = set(resp_values[key])
    answers.difference_update(data_used)

    if not answers:
        # in normal way this block will never execute
        log.W(f'<com.get_resp> answers for ["{key}"] is empty '
              f'(all_vals: {len(resp_values[key])}, data_used:{len(data_used)} )!')
        data_used = [k for k in data_used if k not in resp_values[key]]
        return get_resp(key)

    # if left one phrase -> free all of used
    if len(answers) < 2:
        data_used = [k for k in data_used if k not in resp_values[key]]
    # if left less then 1/4 of phrases -> free half (early) of used
    elif len(answers)-1 < len(resp_values[key]) >> 2:
        # cycle by data_used, because we need order by time of adding
        old_data = [k for k in data_used if k in resp_values[key]]
        free_data = old_data[0:len(old_data) >> 1]
        data_used = [k for k in data_used if k not in free_data]

    ans = other.choice(tuple(answers))
    data_used.append(ans)
    resp_data[ans]['last_key'] = key
    return resp_data[ans]
    #
    # answers = resp_values[key]
    # ans_phr = resp_data[other.choice(answers)]
    # return ans_phr
'''


def get_text_obj(any_keys=None, all_keys=None):
    any_keys = {any_keys} if isinstance(any_keys, str) else (set(any_keys) if any_keys else set())
    all_keys = {all_keys} if isinstance(all_keys, str) else (set(all_keys) if all_keys else set())
    any_k = (any_keys if any_keys else all_keys).copy()
    error_ans = {'text': '', 'last_key': ''}

    if not any_k:
        # log.E('<com.get_text_obj[1]> There are no keys!')
        return error_ans

    texts = set()
    for k in any_k:
        texts.update({h for h in d2u.resp_values.get(k, set()) if d2u.resp_data[h]['keys'].issuperset(all_keys)})

    if not texts:
        # log.E('<com.get_text_obj[2]> There are no keys!')
        return error_ans

    not_used_texts = texts.difference(d2u.data_used)
    # log.D(f'<com.get_text_obj> txts: {len(texts)}, not_used_t: {len(not_used_texts)}, data_used: {len(d2u.data_used)}.')

    if not not_used_texts:
        # log.D(f'<com.get_text_obj> answers for any({", ".join(any_keys)}) and all({", ".join(all_keys)}) '
        #       f'were all used, clear this texts in data_used.')
        d2u.data_used = [k for k in d2u.data_used if k not in texts] # we need order in data_used, so not .difference
        not_used_texts = texts

    ans_h = other.choice(not_used_texts)
    ans = d2u.resp_data[ans_h]
    last_key = other.choice(ans['keys'].intersection(any_keys if any_keys else all_keys))
    ans['last_key'] = last_key

    if not_used_texts != texts:
        for k in ans['keys']:
            topic_t = d2u.resp_values[k]
            topic_unused = topic_t.difference(d2u.data_used)
            if len(topic_t) == len(topic_unused):
                continue
            count_unused = len(topic_unused) - 1
            # log.D(f'<com.get_text_obj> topic_t: {len(topic_t)}, count_unused: {count_unused}.')
            # if left one phrase -> free all of used
            if count_unused < 2:
                # log.D(f'<com.get_text_obj> free all topic_t in data_used ')
                d2u.data_used = [k for k in d2u.data_used if k not in topic_t]
            # if left less then 1/4 of phrases -> free half (early) of used
            elif count_unused <= len(topic_t) >> 2:
                # log.D(f'<com.get_text_obj> free half topic_t in data_used ')
                # cycle by data_used, because we need order by time of adding
                old_data = [k for k in d2u.data_used if k in topic_t]
                data_to_free = old_data[0:len(old_data) >> 1] # early half of used
                d2u.data_used = [k for k in d2u.data_used if k not in data_to_free]

    d2u.data_used.append(ans_h)
    # log.D(f'<com.get_text_obj> data_used: {repr(d2u.data_used)}')
    return ans


def get_t(any_keys=None, all_keys=None, **frm):
    ans = get_text_obj(any_keys, all_keys)
    t = ans.get('text', '') if ans else ''
    if t and frm:
        return t.format(**frm)
    return t


def is_text_exist(any_keys=None, all_keys=None):
    any_keys = {any_keys} if isinstance(any_keys, str) else (set(any_keys) if any_keys else set())
    all_keys = {all_keys} if isinstance(all_keys, str) else (set(all_keys) if all_keys else set())
    any_k = (any_keys if any_keys else all_keys).copy()

    if not any_k:
        return False

    for k in any_k:
        for h in d2u.resp_values.get(k, set()):
            if d2u.resp_data[h]['keys'].issuperset(all_keys):
                return True

    return False


ignore = {'вам', 'всем', 'чат', 'чату', 'чатик', 'чатику', 'в', 'с', 'народ', 'люди', 'сородичи', 'каиниты', 'стая'}
ign_patt = re.compile(rf'((?<!\w)({"|".join(ignore)})(?!\w)([ ]+)?)|((?<=[ ])[ ]+)')


def f_gt_key(orig_phrase, tr_phrase, words, bot_mention):
    """

    :type orig_phrase: basestring
    :type tr_phrase: basestring
    :type words: set
    :param bot_mention: bool
    """
    words.difference_update(emj.em_set)
    words.difference_update(ignore)
    skin_sm = set()
    for w in words:
        if set(w).intersection(emj.skins_set):
            skin_sm.add(w)
    words.difference_update(skin_sm)

    if (orig_phrase.count('@') > 0 and not bot_mention) or len(words) < 1:
        return False

    phr = ign_patt.sub('', tr_phrase)  # delete all words from ignore
    smiles = re.findall(r'[:][\w_]*[:]', orig_phrase)
    count_sm = len(smiles)*2 + ''.join(smiles).count('_')
    simple = len(words) < (count_sm + 2 + bot_mention)
    for g_key in d2u.good_time:
        i = 0
        for g_type in d2u.good_time[g_key]:
            if simple and words.intersection(g_type['simple']):
                return {'g_key': g_key, 'g_type': i}

            for ch_phr in g_type['check_phrases']:
                if ch_phr in phr:
                    return {'g_key': g_key, 'g_type': i}

            i += 1

    return False


def phrase_gt(gt=None, uid=None, add_id=None):
    if not gt:
        return False

    uid = uid or 'here'
    phr = other.choice(d2u.good_time[gt['g_key']][gt['g_type']]['response'])
    str_weather = ''
    if gt['g_key'] == 'g_morn':# and uid in emj.morn_add:
        smile_ids = other.it2list(uid) + other.it2list(add_id)
        smiles = []
        for sm_id in smile_ids:
            smiles += emj.morn_add.get(sm_id, [])
        if smiles:
            phr += ' ' + other.choice(smiles)
    if uid == C.users['Natali'] and gt['g_key'] in ('g_morn', 'g_day'):
        try:
            log.I('try get_weather for Natali')
            str_weather = '\n:newspaper: ' + get_weather()
        except Exception as e:
            other.pr_error(e, 'get_weather')
    return other.name_phr(uid, phr) + str_weather


def get_weather():
    url = 'https://weather.com/ru-RU/weather/5day/l/UPXX0017:1:UP'
    resp = requests__get(url)
    page = lxml__fromstring(resp.content)
    d = page.get_element_by_id('twc-scrollabe')
    tr = d.getchildren()[0].getchildren()[1].getchildren()[0]
    tr_ch = tr.getchildren()
    desc = tr_ch[2].text_content()
    t_max = tr_ch[3].getchildren()[0].getchildren()[0].text_content()
    t_min = tr_ch[3].getchildren()[0].getchildren()[2].text_content()
    rain = tr_ch[4].text_content()
    wind = re.search(r'\d+', tr_ch[5].text_content())[0] # км/ч
    hum = tr_ch[6].text_content()
    t_desc = ''
    if t_min != '--' or t_max != '--':
        t_desc = (' Температура' +
            (' от ' + t_min if t_min != '--' else '') +
            (' до ' + t_max if t_max != '--' else '') +
            '.')
    return ('Во Львове сегодня {descr}.{temp} '
            'Вероятность осадков {rain}, ветер до {wind} км/ч, влажность {hum}.'.format(
        descr=desc.lower(), temp=t_desc, rain=rain, wind=wind, hum=hum))


def hi(uid):
    return other.name_phr(uid, get_t('hello'))


def welcome_msg(uid):
    return '{hi}\n{glad_to_see} {glad_ans} {because} {pause_reason} - {pause_wait} {rules_and_ask}\n{finish}'.format(
        hi=hi(uid), glad_to_see=get_t('glad_to_see'), glad_ans=get_t('glad_ans'), because=get_t('because'),
        pause_reason=get_t('pause_reason'), pause_wait=get_t('pause_wait'),
        rules_and_ask=get_t('rules_and_ask', rules=C.channels['rules'], ask=C.channels['ask']),
        finish=get_t('welcome_finish')
    )


def comeback_msg(uid, time_out=False, clan_id=False):
    return '{0} {1}{2}'.format(get_t('comeback_msg', name=uid),
                               get_t(all_keys={'comeback_time', time_key(time_out)}),
                               clan_id and f"\n{get_t('comeback_clan', clan=clan_id)}" or ''
                               )


def time_key(t):
    if not t:
        return False

    if t < 60:
        return 'min'
    elif t < 3600:
        return 'hour'
    elif t < 86400:     # 3600 * 24
        return 'day'
    elif t < 604800:    # 3600 * 24 * 7
        return 'week'
    elif t < 2592000:   # 3600 * 24 * 30
        return 'month'
    elif t < 15552000:  # 3600 * 24 * 180
        return 'half_year'
    elif t < 31536000:  # 3600 * 24 * 365
        return 'year'
    else:
        return 'years'


def bye(uid, name=''):
    return other.name_phr(uid, get_t('bye'), name=name)


def bye_msg(uid, name=''):
    return '{bye}\n{phrase}'.format(bye=bye(uid, name), phrase=get_t('bye_phrase'))


def ban_msg(uid, nick=''):
    nick = nick and '(' + nick + ')'
    name = '<@{uid}>{nick}'.format(uid=uid, nick=nick)
    return '{msg}\n{comment}'.format(msg=get_t('ban_msg', name=name), comment=get_t('ban_comment'))


def unban_msg(uid):
    return '{msg}\n{comment}'.format(msg=get_t('unban_msg', name=uid), comment=get_t('unban_comment'))


def voice_event(user, channel):
    return get_t('voice_alone_messages', user=f'<@{user.id}>', voice=f'<#{channel.id}>',
                 here=get_t('voice_alone_here'))


def voice_note(user):
    if is_text_exist(all_keys={'voice_notions', user.id}):
        return get_t(all_keys={'voice_notions', user.id}, user=f'<@{user.id}>')
    else:
        return False


def write_msg(ch, text=None, emb=None, extra=0, save_obj=None, fun:callable=None, a_fun:callable=None):
    not_count_sym = {'_', '*', '`'}

    if not text and not emb:
        return ''

    if isinstance(ch, str):
        ch_name = ch
        ch = other.get_channel(ch_name) or other.find_user(ch_name)
        if not ch:
            log.W(f"<write_msg> can't find channel or user {ch_name}.")
            return ''

    if text is None:
        ti, tn = 1, 0
    else:
        ln_text = (len([s for s in text if s not in not_count_sym]) if isinstance(text, str)
                   else sum(len([s for s in txt_i if s not in not_count_sym]) for txt_i in text))
        tn = min(1500, ln_text) / 30 + extra
        ti = 0

    ident = str(other.t2utc().timestamp())
    msg_queue.setdefault(ch.id, []).append(ident)
    msg_args[ident] = (ident, ti, tn, ch, text, emb, save_obj, fun, a_fun)
    # log.D(f'<write_msg>[add] tn = {tn}, ti = {ti}, ident = {ident}.')
    _check_queue(ch.id)
    return ident


def rem_from_queue(ch_id, ids):
    if not ids:
        return
    ids = (ids,) if isinstance(ids, str) else ids
    queue = msg_queue.get(ch_id, [])
    for id_ in ids:
        if id_ in msg_args:
            msg_args.pop(id_)
        if id_ in queue:
            queue.remove(id_)


def _check_queue(ch_id):
    queue = msg_queue.get(ch_id, [])
    if not queue:
        return
    count = msg_type_count.get(ch_id, 0)
    if count < 1:
        if queue[0] in msg_args:
            msg_type_count[ch_id] = msg_type_count.get(ch_id, 0) + 1
            other.later_coro(0, _send_msg(*msg_args.pop(queue[0])))
        else:
            log.W('com._check_queue, lost msg with id ', queue.pop(0))
            _check_queue(ch_id)


async def _send_msg(ident, ti, tn, ch, text=None, emb=None, save_obj=None, fun:callable=None, a_fun:callable=None):

    if ident not in msg_queue.get(ch.id, []):
        msg_type_count[ch.id] = msg_type_count.get(ch.id, 1) - 1
        # log.D(f'<write_msg>[STOP] tn = {tn}, ti = {ti}, ident = {ident}, count = {msg_type_count[ch.id]}.')
        _check_queue(ch.id)
        return

    if ti < tn:
        dt = min(tn - ti, 10)
        # log.D(f'<write_msg>[go] tn = {tn}, ti = {ti}, dt = {dt}, ident = {ident}, count = {msg_type_count[ch.id]}.')
        await C.client.send_typing(ch)
        other.later_coro(dt, _send_msg(ident, ti + dt, tn, ch, text, emb, save_obj, fun, a_fun))
    else:
        try:
            msgs = []
            msg_queue[ch.id].remove(ident)
            msg_type_count[ch.id] = msg_type_count.get(ch.id, 1) - 1
            # log.D(f'<write_msg>[end] ident = {ident}, count = {msg_type_count[ch.id]}.')
            for txt in other.split_text(text):
                msgs.append(await C.client.send_message(ch, content=txt, embed=emb))
            if save_obj is not None:
                if isinstance(save_obj, list):
                    save_obj += msgs
                elif isinstance(save_obj, set):
                    save_obj.update(msgs)
                elif isinstance(save_obj, dict):
                    save_obj[ident] = tuple(msgs)
                elif isinstance(save_obj, tuple): # type (dict, key)
                    save_obj[0][save_obj[1]] = tuple(msgs)
            if fun:
                fun(msgs)
            if a_fun:
                await a_fun(msgs)
        except Exception as e:
            other.pr_error(e, 'com._send_msg', 'Unexpected error')
        finally:
            _check_queue(ch.id)


async def delete_msg(message=None, ch_i=None, msg_id=None, reason='-'):
    if not message:
        try:
            message = await C.client.get_message(other.get_channel(ch_i), msg_id)
        except Exception as e:
            other.pr_error(e, 'com.delete_msg.get_message', 'Unexpected error')
            return
    await other.delete_msg(message, reason)


def text2leet(text, prob=0.25):
    new_text = []
    esc = {'*', '_', '~', '`', '|', '\\',}
    dont_touch = {'#', '@', '&', '<', '>', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    for symb in text:
        if symb in data_com.dct_leet and symb not in dont_touch and other.rand() <= prob:
            new_s = other.choice(data_com.dct_leet[symb]) # type: str
            esc_s = esc.intersection(new_s)
            if esc_s and symb not in esc:
                for s in esc_s:
                    new_s = new_s.replace(s, '\\' + s)
        else:
            new_s = symb
        new_text.append(new_s)
    return ''.join(new_text)


def text2malk(text, prob=0.5):
    if '```' in text:
        return text
    # code style look bad on mobile devices # '`', '**`', '_`', '_`',
    f_set = {'**', '***', '_', '_',} # '~~', # italic more often then others
    esc = {'*', '_', '~', '`', '|', '\\', }
    dont_touch = {'#', '@', '&', '<', '>', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    was_esc = False
    last_f = '0'

    new_text = []
    for i, symb in enumerate(text): # type: int, str
        if symb in string__whitespace or symb in dont_touch:
            new_text.append(symb)
            continue
        elif was_esc and symb in esc:
            was_esc = False
            new_text.append(symb)
            last_f = symb
            continue
        elif symb == '\\':
            next_symb = text[i+1:]
            if next_symb and next_symb[0] in esc:
                was_esc = True
                new_text.append(symb)
            continue
        elif symb in esc:
            continue

        was_esc = False
        if symb != '.' and other.rand() <= prob:
            prob2 = other.rand()
            new_s = symb.upper() if prob2 <= 0.5 else symb
            if prob2 > 0.1:
                f = other.choice({s for s in f_set if s[0] != last_f[0]})
                last_f = f
                new_text.append(f + new_s + f[::-1])
            else:
                last_f = new_s
                new_text.append(new_s)
        else:
            last_f = symb
            new_text.append(symb)

    return ''.join(new_text)
