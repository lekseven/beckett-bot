# -*- coding: utf8 -*-
import re
import random

import data
import local_memory as ram
import beckett_commands as cmd
import constants as C
import emj
import manager
import other
import communication as com


class Msg(manager.Msg):
    def get_commands(self):
        #module_attrs = dir(cmd)
        #cmds = set(key for key in module_attrs if key[0] != '_' and callable(getattr(cmd, key)))
        cmds = cmd.all_cmds.copy()
        if self.channel.id == C.channels['primogens']:
            cmds.intersection_update(cmd.primogenat_cmds)
        elif self.admin and (not self.super or (not self.personal and not self.is_tst)):
            cmds.intersection_update(cmd.admin_cmds)
        elif not self.admin:
            free = cmd.free_cmds
            if {self.author}.intersection({C.users['Creol'], C.users['Tony']}):
                free.add('dominate')
            cmds.intersection_update(free)

        return cmds


async def reaction(message):
    msg = Msg(message)

    if msg.author == C.users['bot']:
        if msg.original == data.tremer_joke:
            other.later_coro(20, msg.delete())
        return

    if msg.torpor:
        await msg.delete()
        return

    if C.roles['Silence'] in msg.roles:
        await msg.delete()
        ram.silence_ans[msg.author] = ram.silence_ans.setdefault(msg.author, 0) + 1
        if ram.silence_ans[msg.author] < 4:
            await msg.answer('Неугодный <@' + msg.author + '> пытается нам нечто сказать, но мы его не слышим...')
        return

    # delete messages containing forbidden links
    if not msg.admin:
        if any(link in msg.text for link in data.forbiddenLinks):
            await msg.delete()
            await msg.answer(random.choice(data.threats).format(name=msg.author))
            return
        '''str = msg.text
        for link in data.forbiddenLinks:
            str = re.sub('(?i)'+link, "**`ЦЕНЗУРА`**", str)
        if str != msg.text:
            await msg.edit(str)
            return'''

    # if we have !cmd -> doing something
    if msg.text.startswith('!'):
        fun = re.match(r'!\w*', msg.text).group(0)[1:]
        if fun in msg.get_commands():
            msg.prepare(fun)
            await getattr(cmd, fun)(msg)
            return
        # if fun and hasattr(cmd, fun):
        #     command = getattr(cmd, fun)
        #     if callable(command) and (fun in C.free_cmds or msg.admin):
        #         msg.prepare(fun)
        #         await command(msg)
        #         return

    embrace_or_return = False
    if (ram.mute_channels.intersection({msg.channel.id, 'all'})
            or msg.author in ram.ignore_users or msg.channel.id in C.ignore_channels):
        if msg.channel.id == C.channels['ask']:
            embrace_or_return = True
        else:
            return

    msg.prepare2()
    beckett_reference = bool(C.beckett_refs.intersection(msg.words))
    beckett_mention = bool(C.beckett_names.intersection(msg.words))  #any(name in msg.args for name in C.beckett_names)
    beckett = beckett_reference or beckett_mention
    # found_keys = check_phrase.check_args(msg.words)
    found_keys = com.check_phrase(msg.text, msg.words)
    prob = random.random()

    # embrace
    if msg.channel.id == C.channels['ask'] and not msg.roles.intersection(C.clan_ids):
        clan_keys = list(C.clan_names.intersection(found_keys))
        if clan_keys:
            other.later_coro(random.randrange(30, 90),
                             manager.do_embrace_and_say(msg, msg.author, clan=random.choice(clan_keys)))
    elif embrace_or_return:
        return

    await emj.on_message(message, beckett)

    if found_keys:
        if not beckett and ram.mute_light_channels.intersection({msg.channel.id, 'all'}):
            return
        response = False

        if prob < 0.2 or beckett_reference or (beckett_mention and (prob < 0.9 or msg.admin)):
            response = True

        if response:
            ans_phr = com.get_resp(found_keys)
            await msg.answer(ans_phr['text'])
            return
    else:
        ans = ''
        if '╯' in msg.original or 'shchupalko' in msg.original:
            if '┻' in msg.original:
                if msg.admin:
                    ans = other.rand_tableflip()
                elif msg.channel.id == C.channels['bar']:
                    if {msg.author}.intersection({C.users['Buffy'], C.users['Tilia'], }):
                        ans = other.rand_tableflip()
                    else:
                        return
                else:
                    ans = '┬─┬ ノ( ゜-゜ノ)'
            else:
                dice_count = msg.original.count('dice') + msg.original.count('🎲')
                if dice_count > 0:
                    ans = other.rand_diceflip(dice_count)
        elif msg.original[1:].startswith('tableflip') and (msg.admin or msg.channel.id == C.channels['bar']):
            ans = '* *бросаю за <@{id}>* *\n{table}'.format(id=msg.author, table=other.rand_tableflip())

        if ans:
            await msg.answer(ans)
            return

        gt = msg.check_good_time(beckett)
        if gt:
            await msg.answer(gt)
            return

        if beckett:
            yes = 'да' in msg.words
            no = 'не' in msg.words or 'нет' in msg.words
            ans = ''
            if msg.words.intersection({'спасибо', 'благодарю'}):    #'спасибо'
                ans = other.name_rand_phr(msg.author, data.sm_resp['wlc'])
            elif msg.words.intersection(data.sm_resp['hi']) or msg.words.intersection(data.sm_resp['hi_smiles']):
                m = data.sm_resp['hi'].copy()
                m += data.sm_resp['hi_smiles'].copy()
                ans = other.name_rand_phr(msg.author, m)
            elif msg.words.intersection(data.sm_resp['bye']):
                ans = other.name_rand_phr(msg.author, data.sm_resp['bye'])
            elif (msg.words.intersection(data.sm_resp['love']) or msg.words.intersection(emj.hearts)) and not no:
                if msg.author == C.users['Natali']:
                    ans = ':purple_heart:'
                else:
                    ans = ':heart:'
                ans = other.name_phr(msg.author, ans)
            elif 'любимый клан' in msg.text:
                if prob > 0.09:
                    ans = random.choice(data.sm_resp['apoliticality'])
                else:
                    ans = data.tremer_joke
            elif msg.words.intersection(data.sm_resp['bot_dog']):
                if msg.admin or prob > 0.2:
                    ans = other.name_rand_phr(msg.author, data.sm_resp['not_funny'])
                else:
                    ans = random.choice(data.threats).format(name=msg.author)
            elif msg.words.intersection({'как'}) and msg.words.intersection({'дела', 'ты'}):
                ans = random.choice(data.responses['whatsup'])
            # other questuons must be before this
            elif msg.text.endswith('?'):
                if msg.admin:
                    if (yes == no) or yes:
                        ans = other.name_rand_phr(msg.author, data.sm_resp['yes'])
                    else:
                        ans = other.name_rand_phr(msg.author, data.sm_resp['no'])
                elif len(msg.args) > 3:
                    ans = random.choice(data.responses['question'])
            elif msg.words.intersection({'скучал', 'скучала', 'скучаль'}):
                ans = other.name_phr(msg.author, 'я тоже')
            elif ('мимими' in msg.text) or len(msg.args) < 4:
                return

            if ans:
                await msg.answer(ans)
                return

        if beckett_reference or (beckett_mention and random.random() < 0.25):
            if msg.author == C.users['Natali'] and prob < 0.4:
                ans_phr = com.get_resp(['For_Prince'])
            else:
                ans_phr = com.get_resp(['beckett'])
            ans = ans_phr['text']
            await msg.answer(ans)
            return
