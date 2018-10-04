import communication as com
import constants as C
import other
import emj
import people
import log
import discord


async def check_server(server, usual_fun, other_fun, *args):
    """
    :type server: discord.Server
    :type usual_fun: Function
    :type other_fun: Function
    """
    if not C.Ready:
        return

    if server.id == C.prm_server.id:
        await usual_fun(*args)
    elif server.id != C.vtm_server.id:
        await other_fun(server, *args)


async def on_member_join_u(member, *args):
    uid = member.id
    if people.Usr.check_new(member):
        await C.client.send_message(C.main_ch, com.comeback_msg(uid, people.time_out(uid), people.clan(uid)))
        await log.pr_news('{0} ({0.mention}) comeback!'.format(member))
    else:
        await C.client.send_message(C.main_ch, com.welcome_msg(uid))
        await log.pr_news('{0} ({0.mention}) new!'.format(member))


async def on_member_join_o(server, member, *args):
    await log.pr_other_news(server, '{0} ({0.mention}) new!'.format(member))


async def on_member_remove_u(member, *args):
    # it's triggers on 'go away', kick and ban
    if not other.find(await C.client.get_bans(C.prm_server), id=member.id):
        people.Gn.check_new(member)
        await C.client.send_message(C.main_ch, com.bye_msg(member.id))
        await log.pr_news('{0} ({0.mention}) go away!'.format(member))


async def on_member_remove_o(server, member, *args):
    await log.pr_other_news(server, '{0} ({0.mention}) go away!'.format(member))


async def on_member_ban_u(member, *args):
    await people.on_ban(member)
    await C.client.send_message(C.main_ch, com.ban_msg(member.id))
    await log.pr_news('Ban {0} ({0.mention})!'.format(member))


async def on_member_ban_o(server, member, *args):
    await log.pr_other_news(server, 'Ban {0} ({0.mention})!'.format(member))


async def on_member_unban_u(user, *args):
    people.on_unban(user)
    await C.client.send_message(C.main_ch, com.unban_msg(user.id))
    await log.pr_news('Unban {0} ({0.mention})!'.format(user))


async def on_member_unban_o(server, user, *args):
    await log.pr_other_news(server, 'Unban {0} ({0.mention})!'.format(user))


async def on_server_emojis_update_u(before, after, *args):
    la = len(after)
    lb = len(before)
    # before, after - list of server emojis
    if la < 1 and lb < 1:
        return
    await log.pr_news('on_server_emojis_update!')
    emj.save_em()


async def on_server_emojis_update_o(server, before, after, *args):
    la = len(after)
    lb = len(before)
    # before, after - list of server emojis
    if la < 1 and lb < 1:
        return
    await log.pr_other_news(server, 'on_server_emojis_update!')


async def on_server_role_create_u(role, *args):
    await log.pr_news('New Role: ' + role.name + '!')


async def on_server_role_create_o(server, role, *args):
    await log.pr_other_news(server, 'New Role: ' + role.name + '!')


async def on_server_role_delete_u(role, *args):
    await log.pr_news('Delete Role: ' + role.name + '!')


async def on_server_role_delete_o(server, role, *args):
    await log.pr_other_news(server, 'Delete Role: ' + role.name + '!')


async def on_server_role_update_u(before, after, *args):
    await log.pr_news('Update Role: ' + before.name + '/' + after.name + '!')


async def on_server_role_update_o(server, before, after, *args):
    await log.pr_other_news(server, 'Update Role: ' + before.name + '/' + after.name + '!')
