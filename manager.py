import operator
import re

import other
import constants as C
import local_memory as ram
import communication as com
import log
import emj
import people


class Msg:

    def __init__(self, message):
        """

        :type message: C.Types.Message
        """
        self.auid = message.author.id
        self.author = message.author # type: C.Types.User
        self.member = C.vtm_server.get_member(self.auid) # type: C.Types.Member
        self.personal = not message.server
        self.cmd_server = ((self.auid in ram.cmd_server and C.client.get_server(ram.cmd_server[self.auid])) or
                           (C.prm_server if self.personal else message.server))
        self.server_id = None if self.personal else message.server.id
        self.is_vtm = self.server_id == C.vtm_server.id
        self.is_tst = self.server_id == C.tst_server.id
        self.message = message
        self.original = message.content or (('≤System≥ ' + message.system_content) if message.system_content else '')
        self.text = message.content.lower().replace('ё', 'е')
        self.args = []
        self.words = set()
        self.channel = message.channel
        self.chid = message.channel.id
        self.roles = {role.id for role in self.member.roles[1:]} if self.member else set()
        self.prince = self.auid == C.users['Natali']
        self.super = self.auid in C.superusers
        self.admin = self.super or self.prince or self.roles.intersection({C.roles['Sheriff'], C.roles['Scourge']})
        self.moder = self.member.server_permissions.administrator if self.member else False
        self.torpor = (not self.prince and self.auid in ram.torpor_users and (
                self.channel.id in ram.torpor_users[self.auid] or 'All' in ram.torpor_users[self.auid]))
        self.cmd_ch = ram.cmd_channels.get(self.auid, set())
        self.rep_ch = ram.rep_channels.get(self.auid, set())
        self.gt = people.get_gt(self.auid)

        self._after_init()

    def _after_init(self):
        if self.is_vtm:
            people.set_last_m(self.auid)

    def prepare(self, fun=''):
        text = self.original[len('!' + fun + ' '):]  #self.text.replace('!' + fun + ' ', '')
        self.args = ([fun] or []) + text.split()
        self.words = set(self.args).difference({'', ' '})

    def prepare2(self, fun=''):
        text = self.text.replace(fun, '')
        em_text = emj.em_set.intersection(text)
        for em in em_text:
            text = text.replace(em, ' ' + em + ' ')
        self.args = ([fun] or []) + text.translate(C.punct2space).split()
        self.words = set(self.args).difference({'', ' '})

    async def delete(self):
        await other.delete_msg(self.message)

    async def edit(self, new_msg):  #not permissions
        await C.client.edit_message(self.message, new_msg)

    @staticmethod
    async def type2sent(ch, text=None, emb=None, extra=0):
        return await other.type2sent(ch, text, emb, extra)

    async def report(self, text):
        for ch_id in self.rep_ch:
            ch = C.client.get_channel(ch_id) or other.find_user(ch_id)
            if ch:
                #await C.client.send_message(ch, text)
                await self.type2sent(ch, text)
        if self.channel.id not in self.rep_ch:
            #await C.client.send_message(self.channel, text)
            await self.type2sent(self.channel, text)

    async def answer(self, text=None, emb=None):
        t = 0
        for txt in other.split_text(text):
            t += await self.type2sent(self.channel, text=txt, emb=emb, extra=t)
        return t

    async def qanswer(self, text):
        for t in other.split_text(text):
            await C.client.send_message(self.channel, t)

    async def say(self, channel, text):
        #await C.client.send_message(channel, text)
        await self.type2sent(channel, text)

    async def purge(self, channel, check_count=1, check=None, aft=None, bef=None):
        try:
            count = int(check_count)
        except Exception as e:
            other.pr_error(e, 'purge')
            await self.qanswer('N должно быть числом!')
            return
        mess_count = 0
        auth = set()
        first, last = None, None
        async for mess in C.client.logs_from(channel, limit=count, before=bef, after=aft):
            if not check or check(mess):
                mess_count += 1
                auth.add(mess.author.id)
                if mess_count == 1:
                    first = mess.timestamp
                    last = mess.timestamp
                else:
                    if first > mess.timestamp:
                        first = mess.timestamp
                    elif last < mess.timestamp:
                        last = mess.timestamp
        if not mess_count:
            await self.qanswer('Не найдено сообщений для purge.')
            return
        else:
            text_mess = 'сообщение' if mess_count == 1 else 'сообшения' if mess_count < 5 else 'сообщений'
            list_auth = other.get_mentions(auth)
            yes = await self.question(
                'Вы уверены что хотите удалить {count} {text_mess} от {list_auth} с {first} по {last} в {channel}? '
                .format(
                    count=mess_count, text_mess=text_mess, list_auth=', '.join(list_auth),
                    first=other.t2s(first, '{%x %X}'), last=other.t2s(last, '{%x %X}'), channel=channel))
            if yes:
                try:
                    await C.client.purge_from(channel, limit=count, check=check, after=aft, before=bef)
                except C.Exceptions.Forbidden:
                    log.jW("Bot haven't permissions here.")
                except Exception as e:
                    other.pr_error(e, 'Msg.purge', 'Unexpected error')
                else:
                    await self.qanswer(":ok_hand:")
            else:
                await self.qanswer("Отмена purge.")

    async def question(self, text):
        yes = {'1', 'y', 'yes', 'да', 'у', '+'}
        await self.qanswer(text + '\n*(для согласия введите 1/y/yes/да/+)*')
        ans = await C.client.wait_for_message(timeout=60, author=self.message.author, channel=self.channel)
        return ans and yes.intersection(ans.content.lower().split())

    def find_member(self, i):
        return other.find_member(self.cmd_server, i)

    def find_members(self, names):
        return other.find_members(self.cmd_server, names)

    def check_good_time(self, beckett):
        gt_key = com.f_gt_key(self.original, self.text, self.words.copy(), beckett)
        if gt_key:
            if people.gt_passed_for(self.auid, gt_key['g_key'], h=18):
                phr = com.phrase_gt(gt_key, self.auid)
                if phr:
                    people.set_gt(self.auid, gt_key['g_key'])
                    return phr
            return ''
        return False

    def get_commands(self):
        # it's rewrite in check_message
        pass


async def turn_silence(user, turn=True, server=None, check=None, force=False):
    change_pr = ('send_messages', 'add_reactions',)
    server = server or C.prm_server
    new_pr = False if turn else None
    check = set(check or ())
    for ch in server.channels:  # type: C.Types.Channel
        if str(ch.type) == 'text':
            bot_prm = ch.permissions_for(server.me)
            if bot_prm.manage_roles:
                add_ch = False
                prm = ch.overwrites_for(user)
                for pr in change_pr:
                    if force or ((turn and getattr(prm, pr) is None) or
                                 (not turn and getattr(prm, pr) is False and ch.id not in check)):
                        setattr(prm, pr, new_pr)
                        add_ch = True
                if add_ch:
                    if prm.is_empty():
                        await C.client.delete_channel_permissions(ch, user)
                    else:
                        await C.client.edit_channel_permissions(ch, user, overwrite=prm)
                else:
                    check.add(ch.id)
    return check


async def silence_on(name, t=1.0, force=False):
    """
    :param name: string
    :param t: float
    :param force: bool
    :rtype: C.Types.Member
    """
    s = C.prm_server
    user = other.find_member(s, name)
    if not user:
        return None

    if user.top_role >= s.me.top_role and not force:
        return False

    t = max(t, 0.02)
    if user.id in ram.silence_users:
        check = ram.silence_users[user.id]['check']
    else:
        check = await turn_silence(user, turn=True, force=force)
    ram.silence_users[user.id] = {'time': other.get_sec_total() + t * 3600 - 1, 'check': tuple(check)}
    if not C.is_test:
        add_roles = [other.find(s.roles, id=C.roles['Silence'])]
        await C.client.add_roles(user, *add_roles)
    log.I('Silence on for ', user, ' at ', other.t2s(), ' on ', t, 'h.')
    return user


async def silence_off(name):
    """
    :param name: string
    :rtype: C.Types.Member
    """
    s = C.prm_server
    user = other.find_member(s, name)
    if not user:
        ram.silence_users.pop(name, 0)
        return None

    s_user = ram.silence_users.pop(user.id, False)
    if s_user:
        await turn_silence(user, turn=False, check=s_user['check'])
        if not C.is_test:
            rem_roles = [other.find(s.roles, id=C.roles['Silence'])]
            await C.client.remove_roles(user, *rem_roles)
        log.I('Silence off for ', user, ' at ', other.t2s())
        return user
    else:
        return False


async def silence_end(name):
    user = await silence_off(name)
    if user:
        await C.client.send_message(C.main_ch, content='<@{0}>, период твоего торпора подошёл к концу.'.format(user.id))
    else:
        log.W('End silence for ', name, ", but can't find user.")


async def voting(channel, text='', timeout=60, votes=None, count=3):
    votes = votes or set()
    text = text + '\n*(для согласия введите за/y/yes/ok//д/да/+/1/:ok_hand:/:thumbsup:)*'
    yes = {'за', '1', 'y', 'yes', 'д', 'да', 'ок', 'у', '+', 't_d_', 'ok_hand', 'ok', 'thumbsup', '+1', 'thumbup'}
    await C.client.send_message(channel, text)
    time_end = other.get_sec_total() + timeout

    def check(msg):
        return (msg.author.id not in votes.union({C.users['bot']}) and
                    yes.intersection(emj.em2text(msg.content).lower().replace('.', '').replace(':', ' ').split()))

    while len(votes) < count:
        time_left = time_end - other.get_sec_total()
        log.I('<voting> We have {0}/{1} votes, wait more for {2} sec.'.format(len(votes), count, time_left))
        ans = await C.client.wait_for_message(timeout=time_left, channel=channel, check=check)
        if ans:
                votes.add(ans.author.id)
                other.later_coro(0, C.client.add_reaction(ans, emj.e('ok_hand')))
        else:
            break
    else:
        return votes

    return False


async def do_check_and_embrace(name, clan_name=None):
    user = other.find_member(C.vtm_server, name)
    if len(user.roles) == 1:
        await just_embrace(user, clan_name=clan_name)
        # just_embrace_say(user, clan_name)
        # text = await do_embrace(user, clan_name=clan_name)
        # com.write_msg(C.main_ch, text)
    else:
        log.D('<do_check_and_embrace> Will not embrace, there are other roles.')


async def just_embrace(user, clan_name=None):
    if not user:
        return False

    if not clan_name:
        for r in user.roles:
            if r.id in C.clan_ids:
                clan_name = C.role_by_id[r.id]
                break
    clan_name = clan_name or other.choice(C.clan_names)
    roles = [r for r in {other.find(C.vtm_server.roles, id=C.roles[clan_name])} if r]
    if clan_name in C.sabbat_clans:
        roles.append(other.find(C.vtm_server.roles, id=C.roles['Sabbat']))
    if roles:
        try:
            await C.client.add_roles(user, *roles)
        except C.Exceptions.Forbidden:
            log.jW("Bot can't change roles.")
        except Exception as e:
            other.pr_error(e, 'do_embrace', 'Error in changing roles')

    return clan_name


def just_embrace_say(user, clan_name, get_text=False):
    if not (user or clan_name):
        return False

    clan_users = set()
    pander = (clan_name == 'Pander')
    sir = None
    if not pander:
        for mem in C.client.get_all_members():
            if other.find(mem.roles, id=C.roles[clan_name]) and mem.id != user.id:
                clan_users.add(mem.id)
        clan_users.difference_update(C.not_sir)
        if clan_users:
            sir = other.choice(list(clan_users))
            text = com.get_t('embrace_msg', sir=f'<@{sir}>', child=f'<@{user.id}>')
        else:
            text = com.get_t('embrace_unic', clan=f'<@&{C.roles[clan_name]}>', child=f'<@{user.id}>')
    else:
        text = com.get_t('embrace_pander', child=f'<@{user.id}>')

    if clan_name in C.sabbat_clans and not pander:
        text += "\n" + com.get_t('embrace_sabbat')

    if get_text:
        return text
    else:
        com.write_msg(C.main_ch, text)
        return sir


# Roll commands

_r_keys = ('s', 'sp', 'p', 'v', 'w', 'f', 'ff')
_f_key = r'(f([-+]?\d+[.,]?\d*)?)'
_p_keys = f'({_f_key}|[a-ce-z| ])' #''.join(set(''.join(_r_keys)))
_s_sum = r'(([ ]*([-+][ ]?)+\d+[.,]?\d*)+(?![d0-9]))'
_roll_gpatt = re.compile(rf'[ ]*(?P<g_sum>{_s_sum})?[ ]*(?P<g_keys>{_p_keys}+)?[ ]*((?![ ])(?P<rolls>.+))?')
_roll_patt = re.compile(rf'''
        [ ]*(?P<sum0>{_s_sum}|[-+])?[ ]*([-+](?![d0-9]))*
        [ ]*(?P<count>[-]?\d+)?(?:[ ]*d[ ]*(?P<type>\d+))?
        [ ]*(?P<sum1>{_s_sum}|[-+])?
        [ ]*(?P<rel>(
            (?P<ge>(>=|=>))|(?P<le>(<=|=<))|(?P<ne>(!=|=!|~=|=~|<>|><|~+|!+|≠))|(?P<eq>[=]+)|(?P<gt>[>]+)|(?P<lt>[<]+)
        ))?
        ([ ]*(?P<diff>[-+]?\d+[.,]?\d*({_s_sum})?)(?![d0-9]))?
        [ ]*(?P<key>{_p_keys}+)?
        ''', re.X)


def _check_flags(prim_flags: set or str=None, sec_flags: set or str=None):
    if not prim_flags and not sec_flags:
        return set()
    res = set()
    prim_flags = prim_flags or set()
    sec_flags = sec_flags or set()
    # Fail keys
    # if 'f' in flags or 'w' in flags:
    #     res.add('f')
    # Specialization keys
    br = False
    for flags in (prim_flags, sec_flags):
        if br:
            break
        br = True
        for fl in ('sp', 'p', 'v', 's',):
            if fl in flags:
                res.add(fl)
                break
        else:
            br = False
    # other keys
    o_keys = ('h',)
    for flags in (prim_flags, sec_flags):
        res.update({k for k in o_keys if k in flags})

    return res


_fail_p = re.compile(_f_key)


def _check_fail(flags:str=None):
    if not flags:
        return None

    f = []
    if 'w' in flags:
        f.append(1)
    if 'f' in flags:
        for m in _fail_p.finditer(flags):
            find = m.group()
            if not find:
                continue
            elif len(find) == 1:
                f.append(1)
            else:
                f.append(other.try_sum(find[1:]))

    return max(f) if f else None


def get_dice_param(text, add_keys=''):
    err = True, *(None,) * 6
    m = _roll_gpatt.search(text)
    error = not m or False
    if error:
        return err

    g_group = m.groupdict()
    error = not g_group['rolls']
    if error:
        return err

    rel_keys = ('ge', 'le', 'ne', 'eq', 'gt', 'lt')
    g_flags = _check_flags(add_keys, g_group['g_keys'])
    g_fail = _check_fail((g_group['g_keys'] or '') + add_keys)
    g_sum = other.try_sum(g_group['g_sum'])
    counts, dtypes, rolls_args = [], [], [],
    all_flags = g_flags.copy()
    calc_sum = False
    simple = True
    not_simple_fl = False
    inv_next = False

    for m in _roll_patt.finditer(g_group['rolls']):
        group = m.groupdict()
        if not any((group['count'], group['type'], group['rel'], group['diff'])):
            break
        inv_now = inv_next
        par_keys = _check_flags(group['key'], g_flags)
        all_flags.update(par_keys)
        d_fail = _check_fail(group['key'])
        d_fail = g_fail if d_fail is None else d_fail

        if group['count'] and group['count'][0] == '-':
            inv_now = not inv_now
            group['count'] = group['count'][1:]
        count = other.obj2int(group['count']) or 1
        dtype = other.obj2int(group['type']) or 10
        if group['sum0'] and (group['sum0'][-1] == '-' or group['sum0'][-1] == '+'):
            if group['sum0'][-1] == '-':
                inv_now = not inv_now
            group['sum0'] = group['sum0'][:-1]
        sum0 = other.try_sum(group['sum0']) if group['sum0'] else g_sum
        sum1 = other.try_sum(group['sum1'])
        inv_next = group['sum1'] and group['sum1'][-1] == '-'
        rel = [key for key in rel_keys if group[key]][0] if group['rel'] else None  #'ge'
        diff = other.try_sum(group['diff']) if group['diff'] else None  #int(dtype / 2 + 1)

        calc_sum = calc_sum or bool(group['sum1'])
        not_simple_fl = not_simple_fl or par_keys.intersection({'v', 'sp', 'p', 's'}) or (d_fail is not None)
        simple = simple and not any((group['rel'], group['diff'], ))
        counts.append(count)
        dtypes.append(dtype)
        rolls_args.append((count, dtype, par_keys, rel, diff, sum0, sum1, d_fail, inv_now))

    error = not all((counts, dtypes, rolls_args))
    if error:
        return err

    simple = simple and (calc_sum or not not_simple_fl)

    return error, sum(counts), max(dtypes), ''.join(all_flags), simple, calc_sum, rolls_args


def _get_symb(change_val, short=False):

    if short:
        if change_val > 0:
            symb = '`'
        elif change_val < 0:
            symb = '**'
        else:
            symb = '~~'
    else:
        if change_val > 0:
            symb = '+'
        elif change_val < 0:
            symb = '-'
        else:
            symb = '•'
    return symb


def get_dice(count=1, dtype=10, par_keys:set='', rel='ge', diff=6,
               sum0=0, sum1=0, d_fail=None, inv=False, simple=True, short=False, calc_sum=False):
    return get_dices([(count, dtype, par_keys, rel, diff, sum0, sum1, d_fail, inv, )],
                     short=short, simple=simple, calc_sum=calc_sum)


def get_dices(rolls_args:list, short=False, simple=True, calc_sum=False):

    rel_keys = {'ge': '>=', 'le': '<=', 'ne': '!=', 'eq': '==', 'gt': '>', 'lt': '<'}
    text = []
    if not rolls_args:
        return text

    not_one = len(rolls_args) > 1
    if short:
        add_symb = '+' if calc_sum else '&'
    else:
        add_symb = '+++ ' if calc_sum else '*** '

    res = []
    was_success = False
    for i, args in enumerate(rolls_args):
        count, dtype, par_keys, rel, diff, sum0, sum1, d_fail, inv = args
        dice_simple = (diff is None and rel is None) if calc_sum else simple
        diff = int(dtype / 2 + 1) if diff is None else diff
        rel = 'ge' if rel is None else rel

        symb = ('-' if short else '--- ') if inv else add_symb
        if not_one:
            if short:
                if i > 0 or inv:
                    text.append(symb)
            else:
                rel_diff = '' if dice_simple else f' {rel_keys[rel]} {diff}'
                dice_type = f'[{1+sum0},{dtype+sum0}]' if sum0 != 0 else dtype
                add = ('+' if sum1 == 0 else f'{sum1:+}') if calc_sum else ''
                flags = (' ' + ''.join(par_keys)) if par_keys else ''
                flags += (('' if flags else ' ') + f'f{d_fail}') if d_fail is not None else ''
                s_inv = '-' if inv else ''
                text.append(f'{symb}{s_inv}{count}d{dice_type}{add}{rel_diff}{flags}:\n')
        elif inv and short:
            text.append(symb)

        args = count, dtype, par_keys, rel, diff, sum0, sum1, d_fail,
        d_text, d_res, d_was_success = get_rolles(*args, short=short, simple=dice_simple, calc_sum=calc_sum)
        res.append(-d_res if inv else d_res)
        was_success = was_success or d_was_success
        text += d_text

    # total result
    if simple and not calc_sum:
        return text

    res = sum(res)
    if calc_sum:
        symb = '-' if res < 0 else '!' if res > 0 else '***'
        conclusion = f'= {res}' if short else f'{symb} Итого: {res}.'
    elif short:
        text[-1] += ':'
        conclusion = ('**`успех ({})`**' if res > 0 else
                      'неудача' if (not not_one and (was_success or res == 0)) else
                      'неудача ({})' if (not_one and (was_success or res == 0)) else
                      '**провал ({})**').format(res)
    else:
        conclusion = ('! Успех ({})' if res > 0 else
                      '• Неудача' if (not not_one and (was_success or res == 0)) else
                      '• Неудача ({})' if (not_one and (was_success or res == 0)) else
                      '- Провал ({})').format(res)
        conclusion += '\n'
    text.append(conclusion)

    return text


def get_rolles(count=1, dtype=10, par_keys:set='', rel='ge', diff=6,
               sum0=0, sum1=0, d_fail=None, simple=True, short=False, calc_sum=False, _add_d=False):
    text = []
    dices = []
    res = 0
    was_success = False

    for i in range(0, count):
        d = other.rand(1, dtype)
        dices.append(d)

    if simple and not calc_sum:
        if short:
            text = [str(dice+sum0) for dice in dices]
        else:
            text = ['{:02d}d:\t{val}\n'.format(i + 1, val=dice+sum0) for i, dice in enumerate(dices)]
    else:
        if short and not _add_d:
            text.append('(')
        add_dices = 0
        double_ten = False
        for i, dice in enumerate(dices):
            succ = simple or getattr(operator, rel)(dice+sum0, diff)
            aft = ''
            # process one dice
            if succ:
                change_val = (dice + sum0) if calc_sum else +1
                res += change_val
                was_success = True
                if dice == dtype and dtype > 1 and par_keys:
                    if 'sp' in par_keys:
                        res += change_val
                        aft = '(+)'
                    elif 'p' in par_keys:
                        aft = double_ten and '(+)' or ''
                        res += int(double_ten) * change_val
                        double_ten = not double_ten
                    elif 'v' in par_keys:
                        aft = double_ten and '(++)' or ''
                        res += 2 * int(double_ten) * change_val
                        double_ten = not double_ten
                    elif 's' in par_keys:
                        add_dices += 1
                        aft = '(*)'
                change_val = +1
            else:
                change_val = 0
                if d_fail is not None and (dice + sum0) <= d_fail:
                    change_val = -(dice + sum0) if calc_sum else -1
                    res += change_val
                    change_val = -1
            # text format
            if short:
                if calc_sum:
                    if i > 0 or change_val < 0:
                        text.append('+' if change_val >= 0 else '-')
                symb = '' if simple else _get_symb(change_val, True)
                symb2 = '__**' if aft else ''
                text.append('{symb2_1}{symb}{val}{symb}{symb2_2}'.
                            format(symb=symb, val=dice+sum0, symb2_1=symb2, symb2_2=symb2[::-1]))
            else:
                symb = ('!' if aft else '•') if simple else _get_symb(change_val)
                aft = ' ' + aft if aft else ''
                text.append('{} {:02d}d:\t{val}{aft}\n'.format(symb, i+1, val=dice+sum0, aft=aft))
        # process add_dices
        if _add_d:
            return res, text, add_dices
        while add_dices:
            if short:
                text.append(r'\|{}\| \*__{{{}}}__:'.format(r'\|+\|' if calc_sum else '', add_dices))
            else:
                text.append('*** Специализация({}):\n'.format(add_dices))
            (add_res, add_text, add_dices) = get_rolles(add_dices, dtype, par_keys, rel, diff, sum0, sum1, d_fail,
                                                        short=short, simple=simple, calc_sum=calc_sum, _add_d=True)
            res += add_res
            text += add_text
        # total result
        if sum1 != 0:
            res += sum1
            symb = '+' if sum1 > 0 else '-'
            text.append(f') {sum1:+}' if short else f'{symb} add:\t{sum1:+}\n')
        elif short:
            text.append(')')

    return text, res, was_success


_v5_patt = re.compile(r'''
        [ ]*(?P<key1>[a-zA-Z_]+)?
        [ ]*(?P<count>\d+)?
        ([ ]+(?P<diff>\d+))?
        ([ ]+(?P<hung>\d+))?
        [ ]*(?P<key2>[a-zA-Z_]+)?
        ''', re.X)


def get_v5_param(text, add_keys=''):
    count, diff, hung, par_keys, simple = None, 0, 0, None, None
    m = _v5_patt.search(text)
    error = not m or False
    if not error:
        group = m.groupdict()
        error = not group['count']

        if not error:
            par_keys = (group['key1'] or '') + (group['key2'] or '') + add_keys
            count = int(group['count']) or 1
            simple = not group['diff']
            if not simple:
                diff = int(group['diff']) if group['diff'] else 0
                hung = int(group['hung']) if group['hung'] else 0

    return error, count, diff, hung, par_keys, simple


def _get_val_v5(dice, hunger=False, short=False):
    hunger = bool(hunger)
    short = bool(short)
    if dice == 10:
        symb = (('☘', r'\🍀'), ('☿', '👹'))[hunger][short]
    elif dice > 5:
        symb = '☥'
    elif hunger and dice == 1:
        symb = ('☠', '💀')[short]
    else:
        symb = ('●', '•')[short]

    if hunger and short:
        symb = '`' + symb + '`'
    return symb


def get_dices_v5(count=1, diff=0, hung=0, simple=False, short=False):
    text = []
    dices = []
    count_tens = 0
    for i in range(0, count):
        d = other.rand(1, 10)
        dices.append(d)
        count_tens += 1 if d == 10 else 0

    if simple:
        if short:
            text = ['{val}'.format(val=_get_val_v5(dice, short=True)) for dice in dices]
        else:
            text = ['{:02d}d:\t{val}\n'.format(i + 1, val=_get_val_v5(dice)) for i, dice in enumerate(dices)]
    else:
        if short:
            text.append('(')
        was_h1 = False
        was_h10 = False
        res = 0
        crit_tens = int(count_tens/2)*2
        norm_dices = max(count - hung, 0) # other: hung_dices
        for i, dice in enumerate(dices):
            hunger = i >= norm_dices
            succ = dice > 5
            aft = ''
            if succ:
                res += 1
                if dice == 10:
                    if crit_tens > 0:
                        aft = ' (+)'
                        res += 1
                        crit_tens -= 1
                    symb = '!'
                    was_h10 = hunger or was_h10
                else:
                    symb = '+'
            else:
                symb = '•'
                was_h1 = was_h1 or (hunger and dice == 1)
            symb = '-' if hunger else symb
            if short:
                if hunger and i == norm_dices:
                    text.append(r'\|\|')
                frm = '__' if aft else ''
                text.append('{frm}{val}{frm}'.format(val=_get_val_v5(dice, hunger, short=True), frm=frm))
            else:
                text.append('{} {:02d}d:\t{val}{aft}\n'.format(symb, i + 1, val=_get_val_v5(dice, hunger), aft=aft))

        if res >= diff:
            if count_tens > 1:
                conclusion = (('- {}', '**__`{}`__**')[short].format('Messy Critical')
                              if was_h10 else ('! {}', '**__{}__**')[short].format('Critical Win'))
            else:
                conclusion = ('+ {}', '**{}**')[short].format('Success') #'+ Win'
            conclusion = ('{} ({} {})', '{} *({} {})*')[short].format(conclusion, 'margin:', res - diff)
        else:
            if was_h1:
                conclusion = ('- {}', '**`{}`**')[short].format('Bestial Failure')
            elif res > 0:
                conclusion = ('• {} ({} {})', '{} *({} {})*')[short].format('Failure', 'win at a cost:', diff - res)
            else:
                conclusion = ('● {}', '{}')[short].format('Total Failure')

        if short:
            text.append('):')
        text.append(conclusion)
    return text
